import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="초등교사를 위한 학급 성적 관리 프로그램",
    page_icon="📊",
    layout="wide",
)

st.title("📊 초등교사를 위한 학급 성적 관리 프로그램")
st.caption("날짜, 단원명, 학생 이름, 점수 4개 컬럼으로 업로드된 데이터를 시각화합니다.")

# ===== 공용 유틸 (인코딩 자동 처리) =====
def read_csv_any(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.read()
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8", errors="replace")

with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("학생 점수 CSV 파일 (날짜, 단원명, 학생 이름, 점수 4개 컬럼)", type=["csv", "xls", "xlsx"])
    st.markdown("""
    **필수 컬럼 (순서 상관 없음, 컬럼명 반드시 정확하게!)**
    - 날짜
    - 단원명
    - 학생 이름
    - 점수
    """)

if uploaded is None:
    st.info("👈 왼쪽에서 학생 점수 파일(.csv/.xls/.xlsx)을 업로드하세요.")
    st.stop()

if uploaded.name.endswith(".csv"):
    df_raw = read_csv_any(uploaded)
else:
    df_raw = pd.read_excel(uploaded)

required_cols = {"날짜", "단원명", "학생 이름", "점수"}
if not required_cols.issubset(set(df_raw.columns)):
    st.error(f"다음 4개 컬럼이 모두 포함되어야 합니다: {required_cols}")
    st.stop()

df_raw["점수"] = pd.to_numeric(df_raw["점수"], errors="coerce")
df = df_raw.dropna(subset=["날짜", "단원명", "학생 이름", "점수"])

# ===== 1. 학생별 × 단원명별 피벗 =====
st.subheader("① 전체 학생 × 단원별 점수표 (반 평균 포함)")

pivot_df = df.pivot_table(
    index="학생 이름",
    columns="단원명",
    values="점수",
    aggfunc="mean"
)

# 학생별 평균 추가
pivot_df["학생평균"] = pivot_df.mean(axis=1)
# 단원별 평균(컬럼)
unit_means = pivot_df.mean(axis=0)
# 평균 행을 시리즈로 생성 — 인덱스명: '반평균'
pivot_df_withmean = pd.concat([pivot_df, pd.DataFrame([unit_means], index=["반평균"])])

def highlight_cells(s):
    if s.name == "반평균":  # 평균행
        return ["background-color: #F9DC5C; font-weight: bold;"] * len(s)
    if pd.isna(s["학생평균"]):
        return ["" for _ in s]
    # 각 학생 행에 대해
    class_mean = unit_means["학생평균"]
    out = []
    for col, val in s.items():
        if col == "학생평균":
            if val >= class_mean:
                out.append("background-color: #53bfff;")
            else:
                out.append("background-color: #fc8282;")
        else:
            m = unit_means[col]
            if pd.isna(val):
                out.append("")
            elif val >= m:
                out.append("background-color: #b7e1fa;")
            else:
                out.append("background-color: #ffcad4;")
    return out

st.dataframe(
    pivot_df_withmean.style.apply(highlight_cells, axis=1),
    use_container_width=True,
    hide_index=False,
)

# ===== 2. 단원별 점수 내림차순 =====
st.subheader("② 단원별 점수 내림차순 (학생별)")

select_unit = st.selectbox("단원명을 선택하세요:", [c for c in pivot_df.columns if c != "학생평균"])
if select_unit:
    unit_scores = df[df["단원명"] == select_unit][["학생 이름", "점수"]].sort_values(by="점수", ascending=False)
    st.dataframe(unit_scores.reset_index(drop=True), use_container_width=True, hide_index=True)

# ===== 3. 학생별 점수 요약 및 그래프 =====
st.subheader("③ 학생별 단원별 점수 및 평균 그래프")

student_list = [i for i in pivot_df.index if i != "반평균"]
selected_student = st.selectbox("학생을 선택하세요:", student_list)

if selected_student:
    student_scores = pivot_df.loc[selected_student].drop("학생평균")
    avg_scores = unit_means.drop("학생평균")
    summary_df = pd.DataFrame({
        "단원명": avg_scores.index,
        "학생 점수": student_scores.values,
        "단원별 평균": avg_scores.values
    })
    st.write(f"**{selected_student} 학생의 단원별 점수 요약**")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.line_chart(summary_df.set_index("단원명")[["학생 점수", "단원별 평균"])
