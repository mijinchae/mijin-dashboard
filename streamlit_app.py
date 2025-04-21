# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="회원구분별 매출 변화 분석", layout="wide")

# 구글 드라이브 파일 ID
file_id = "1vlOddDEvMy1M4aRola3RbZIIxLH8srdh"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

@st.cache_data
def load_data():
    df = pd.read_excel(url, sheet_name=0)
    return df

df = load_data()

# 기본 설정
MEMBER_OPTIONS = ['일반', '오프셋', '학위논문', '전체']
TYPE_OPTIONS = ['신규', '기존', '신규+기존']

# 회원/구분 선택 (초기 세팅 변경)
selected_member = st.selectbox("회원 구분을 선택하세요", MEMBER_OPTIONS, index=3)
selected_type = st.selectbox("신규/기존을 선택하세요", TYPE_OPTIONS, index=2)

# 데이터 필터링 함수
def filter_data(df, year):
    df_filtered = df[df['연도'] == year]
    if selected_member != '전체':
        df_filtered = df_filtered[df_filtered['주문'] == selected_member]
    if selected_type != '신규+기존':
        df_filtered = df_filtered[df_filtered['구분'] == selected_type]
    return df_filtered.reset_index(drop=True)

filtered_2023 = filter_data(df, 2023)
filtered_2024 = filter_data(df, 2024)

# 총합 계산
total_2023 = {
    '명': filtered_2023['명'].sum(),
    '건': filtered_2023['건'].sum(),
    '매출': filtered_2023['매출'].sum()
}
total_2024 = {
    '명': filtered_2024['명'].sum(),
    '건': filtered_2024['건'].sum(),
    '매출': filtered_2024['매출'].sum()
}

# 📊 총합 변화 카드 스타일 출력
st.subheader("📊 총합 변화 (2023 → 2024)")

kpi_cols = st.columns(3)
metrics = ['명', '건', '매출']

for idx, metric in enumerate(metrics):
    prev = total_2023[metric]
    curr = total_2024[metric]
    diff = curr - prev
    growth = ((curr - prev) / prev) * 100 if prev != 0 else 0
    color = "🟢" if diff >= 0 else "🔴"

    with kpi_cols[idx]:
        st.markdown(f"""
        <div style="padding:1rem; border-radius:10px; background-color:#f9f9f9; text-align:center">
            <div style="font-size:14px; color:gray">2023: {int(prev):,} → 2024: {int(curr):,}</div>
            <div style="font-size:24px; font-weight:bold; color:black; margin-top:0.5rem">{diff:+,} {color}</div>
            <div style="font-size:14px; color:gray; margin-top:0.5rem">📈 성장률: {growth:+.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

# 🧩 매출 비율 (2024)
st.subheader("🧩 매출 비율 (2024)")

# 원형 차트
if selected_member == '전체':
    member_sales = {}
    for member in ['일반', '오프셋', '학위논문']:
        member_sales[member] = df[(df['연도'] == 2024) & (df['주문'] == member)]['매출'].sum()

    sales_df = pd.DataFrame({
        '구분': list(member_sales.keys()),
        '매출': list(member_sales.values())
    })

    colors = ["#A7D3F5", "#D4C1EC", "#C7E8C9"]

    fig = px.pie(
        sales_df,
        names='구분',
        values='매출',
        hole=0.5,
        color_discrete_sequence=colors
    )

else:
    type_sales = {}
    for t in ['신규', '기존']:
        type_sales[t] = df[(df['연도'] == 2024) & (df['주문'] == selected_member) & (df['구분'] == t)]['매출'].sum()

    sales_df = pd.DataFrame({
        '구분': list(type_sales.keys()),
        '매출': list(type_sales.values())
    })

    color_map = {
        '신규': '#A7D3F5',
        '기존': '#D4C1EC'
    }

    fig = px.pie(
        sales_df,
        names='구분',
        values='매출',
        hole=0.5,
        color='구분',
        color_discrete_map=color_map
    )

fig.update_layout(
    title_x=0.5,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# 📈 월별 추이 그래프
st.subheader("📈 월별 추이 비교 (2023 vs 2024)")

for metric in metrics:
    chart_data = []
    for month in [4,5,6,7,8,9,10,11,12,1,2,3]:
        value_2023 = filtered_2023[filtered_2023['월'] == month][metric].sum()
        value_2024 = filtered_2024[filtered_2024['월'] == month][metric].sum()

        chart_data.append({
            "표시월": f"{month}월",
            "구분": "2023회계연도",
            "값": value_2023,
            "지표": metric
        })

        chart_data.append({
            "표시월": f"{month}월",
            "구분": "2024회계연도",
            "값": value_2024,
            "지표": metric
        })

    chart_df = pd.DataFrame(chart_data)

    fig = px.line(
        chart_df,
        x="표시월",
        y="값",
        color="구분",
        markers=True,
        title=f"{metric} 월별 추이",
        category_orders={"표시월": [f"{m}월" for m in [4,5,6,7,8,9,10,11,12,1,2,3]]}
    )

    fig.update_layout(
        title_x=0.5,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
