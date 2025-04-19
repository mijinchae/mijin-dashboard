# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="회원구분별 매출 변화 분석", layout="wide")

# 구글 드라이브 파일 ID
file_id = "1vlOddDEvMy1M4aRola3RbZIIxLH8srdh"

# 구글 드라이브 다운로드 URL 만들기
url = f"https://drive.google.com/uc?export=download&id={file_id}"

@st.cache_data
def load_data():
    df_2023 = pd.read_excel(url, sheet_name="월별데이터(2023)")
    df_2024 = pd.read_excel(url, sheet_name="월별데이터(2024)")
    return df_2023, df_2024

df_2023, df_2024 = load_data()

# 기본 설정
MEMBER_OPTIONS = ['일반', '오프셋', '학위논문', '전체']
TYPE_OPTIONS = ['신규', '기존', '신규+기존']

# 컬럼 설정
member_column_2023 = df_2023.columns[0]
type_column_2023 = df_2023.columns[1]
member_column_2024 = df_2024.columns[0]
type_column_2024 = df_2024.columns[1]

# 회원/구분 선택 (초기 세팅 변경)
selected_member = st.selectbox("회원 구분을 선택하세요", MEMBER_OPTIONS, index=3)  # '전체' 기본
selected_type = st.selectbox("신규/기존을 선택하세요", TYPE_OPTIONS, index=2)    # '신규+기존' 기본

def filter_data(df, member_col, type_col):
    if selected_member == '전체':
        df_filtered = df[df[type_col].isin(['신규', '기존'])]
    else:
        if selected_type == '신규+기존':
            df_filtered = df[(df[member_col] == selected_member) & (df[type_col].isin(['신규', '기존']))]
        else:
            df_filtered = df[(df[member_col] == selected_member) & (df[type_col] == selected_type)]
    return df_filtered.reset_index(drop=True)

filtered_2023 = filter_data(df_2023, member_column_2023, type_column_2023)
filtered_2024 = filter_data(df_2024, member_column_2024, type_column_2024)

# 총합 계산
total_2023 = {
    '명': filtered_2023['2023_총합_명'].sum(),
    '건': filtered_2023['2023_총합_건'].sum(),
    '매출': filtered_2023['2023_총합_매출'].sum()
}
total_2024 = {
    '명': filtered_2024['2024_총합_명'].sum(),
    '건': filtered_2024['2024_총합_건'].sum(),
    '매출': filtered_2024['2024_총합_매출'].sum()
}

# 📊 총합 변화 카드 스타일 출력
st.subheader("📊 총합 변화 (2023 → 2024)")

kpi_cols = st.columns(3)
metrics = ['명', '건', '매출']

for idx, metric in enumerate(metrics):
    prev = total_2023[metric]
    curr = total_2024[metric]
    diff = curr - prev
    color = "🟢" if diff >= 0 else "🔴"

    with kpi_cols[idx]:
        st.markdown(f"""
        <div style="padding:1rem; border-radius:10px; background-color:#1a1a1a; text-align:center">
            <div style="font-size:14px; color:lightgray">2023: {int(prev):,} → 2024: {int(curr):,}</div>
            <div style="font-size:24px; font-weight:bold; color:white; margin-top:0.5rem">{diff:+,} {color}</div>
        </div>
        """, unsafe_allow_html=True)

# 🧩 매출 비율 (2024)
st.subheader("🧩 매출 비율 (2024)")

if selected_member == '전체':
    member_sales = {}
    for member in ['일반', '오프셋', '학위논문']:
        filtered_member = filtered_2024[filtered_2024[member_column_2024] == member]
        member_sales[member] = filtered_member['2024_총합_매출'].sum()

    sales_df = pd.DataFrame({
        '구분': list(member_sales.keys()),
        '매출': list(member_sales.values())
    })
else:
    type_sales = {}
    for t in ['신규', '기존']:
        filtered_type = filtered_2024[(filtered_2024[member_column_2024] == selected_member) & (filtered_2024[type_column_2024] == t)]
        type_sales[t] = filtered_type['2024_총합_매출'].sum()

    sales_df = pd.DataFrame({
        '구분': list(type_sales.keys()),
        '매출': list(type_sales.values())
    })

# 블루톤 색상 설정
colors = ["#1f77b4", "#3399ff", "#66b2ff"]

fig = px.pie(
    sales_df,
    names='구분',
    values='매출',
    hole=0.5,
    color_discrete_sequence=colors
)
fig.update_layout(
    plot_bgcolor="black",
    paper_bgcolor="black",
    font_color="white",
    title_font_color="white",
    legend_font_color="white",
    title_x=0.5,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# 📈 월별 추이 그래프
st.subheader("📈 월별 추이 비교 (2023 vs 2024)")

for metric in metrics:
    chart_data = []
    for month in [4,5,6,7,8,9,10,11,12,1,2,3]:
        if month >= 4:
            fiscal_month = month - 3
        else:
            fiscal_month = month + 9

        if month >= 4:
            col_2023 = f"2023_{month}_{metric}"
            col_2024 = f"2024_{month}_{metric}"
        else:
            col_2023 = f"2024_{month}_{metric}"
            col_2024 = f"2025_{month}_{metric}"

        if col_2023 in filtered_2023.columns:
            value_2023 = pd.to_numeric(filtered_2023[col_2023], errors='coerce').sum()
            chart_data.append({
                "회계월": fiscal_month,
                "표시월": f"{month}월",
                "구분": "2023회계연도",
                "값": value_2023,
                "지표": metric
            })

        if col_2024 in filtered_2024.columns:
            value_2024 = pd.to_numeric(filtered_2024[col_2024], errors='coerce').sum()
            chart_data.append({
                "회계월": fiscal_month,
                "표시월": f"{month}월",
                "구분": "2024회계연도",
                "값": value_2024,
                "지표": metric
            })

    chart_df = pd.DataFrame(chart_data)
    chart_df = chart_df.sort_values("회계월")

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
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        title_font_color="white",
        legend_font_color="white",
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
