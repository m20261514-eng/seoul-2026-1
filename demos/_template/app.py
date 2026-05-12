import io
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="초등교사를 위한 학급 성적 관리 프로그램",
    page_icon="📊",
    layout="wide",
)

st.title("📊 초등교사를 위한 학급 성적 관리 프로그램")
st.caption("엑셀 파일을 업로드하면 학생 점수와 평균을 색상 및 그래프로 시각화합니다.")

# ===== 공용 유틸 (인코딩 자동 처리) =====
def read_csv_any(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.read()
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8", errors="replace")

# ===== 1. 사이드바: 파일 업로더 =====
with st.sidebar:
    st.header("📂 데이터 업로드")
    uploaded = st.file_uploader("학생 점수 CSV 파일", type=["csv", "xls", "xlsx"])
    st.markdown("""
    **필수 컬럼**
    - `이름` (학생명)
    - 각 과목 혹은 단원명 (열마다)
    - 예시: 이름, 국어, 수학, 과학 ...
    """)

if uploaded is None:
    st.info("👈 왼쪽에서 학생 점수 파일(.csv/.xls/.xlsx)을 업로드하세요.")
    st.stop()

# 파일 확장자 구분
if uploaded.name.endswith(".csv"):
    df = read_csv_any(uploaded)
else:
    df = pd.read_excel(uploaded)

# 과목/단원 추출 (첫 번째 컬럼은 '이름'으로 가정)
unit_columns = [col for col in df.columns if col != "이름"]

# ===== 1. (기능1) 표 + 평균행 + 셀 색상 =====
st.subheader("① 전체 학생 점수 테이블")

df_numeric = df.copy()
df_numeric[unit_columns] = df_numeric[unit_columns].apply(pd.to_numeric, errors="coerce")

# 학생별 평균 점수 컬럼 추가
df_numeric["학생평균"] = df_numeric[unit_columns].mean(axis=1)
# 반 전체 평균 (각 단원/과목별 평균)
unit_means = df_numeric[unit_columns].mean(axis=0)
class_mean = df_numeric["학생평균"].mean()

# 평균 행 추가
mean_row = ["반평균"] + list(unit_means) + [class_mean]
display_df = pd.concat([df_numeric, pd.DataFrame([mean_row], columns=df_numeric.columns)], ignore_index=True)

# 셀 색상 함수
def highlight_cells(row):
    is_mean_row = row["이름"] == "반평균"
    styles = []
    for col in display_df.columns:
        if col == "이름":
            styles.append("font-weight: bold;" if is_mean_row else "")
        elif col == "학생평균":
            if is_mean_row:
                styles.append("background-color: #F9DC5C; font-weight: bold;")
            elif pd.isna(row[col]):
                styles.append("")
            elif row[col] >= class_mean:
                styles.append("background-color: #53bfff;")
            else:
                styles.append("background-color: #fc8282;")
        else:
            if is_mean_row:
                styles.append("background-color: #F9DC5C; font-weight: bold;")
            elif pd.isna(row[col]):
                styles.append("")
            elif row[col] >= unit_means[col]:
                styles.append("background-color: #b7e1fa;")
            else:
                styles.append("background-color: #ffcad4;")
    return styles

st.dataframe(
    display_df.style.apply(highlight_cells, axis=1), 
    use_container_width=True, 
    hide_index=True
)

# ===== 2. (기능2) 단원별 점수 정렬 및 선택 =====
st.subheader("② 단원별 점수 확인 (클릭 시 정렬)")

selected_unit = st.selectbox("단원을 선택하세요:", unit_columns)
if selected_unit:
    sorted_df = df_numeric.sort_values(by=selected_unit, ascending=False)
    st.write(f"**[{selected_unit}] 점수 내림차순 정렬**")
    st.dataframe(
        sorted_df[["이름", selected_unit]],
        use_container_width=True, 
        hide_index=True
    )

# ===== 3. (기능3) 학생별 점수 추이 및 비교 =====
st.subheader("③ 학생별 점수 요약과 그래프")

student_names = df_numeric["이름"][df_numeric["이름"] != "반평균"].unique().tolist()
selected_student = st.selectbox("학생을 선택하세요:", student_names)

if selected_student:
    student_scores = df_numeric[df_numeric["이름"] == selected_student][unit_columns].iloc[0]
    avg_scores = unit_means

    summary_df = pd.DataFrame({
        "단원명": unit_columns,
        "학생 점수": student_scores.values,
        "단원별 평균": avg_scores.values
    })

    st.write(f"**{selected_student} 학생의 단원별 점수 요약**")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # 꺾은선 그래프
    st.line_chart(
        summary_df.set_index("단원명")["학생 점수 단원별 평균".split()]
    )
