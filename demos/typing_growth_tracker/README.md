# ⌨️ 타자 성장 트래커 (Typing Growth Tracker)

학생들의 1·2·3회차 타자 속도 변화를 그래프와 성장 퍼센티지로 시각화해주는 도구.
**결과보다 성장 과정**에 초점을 둔 평가 보조 앱입니다.

> 2026-1학기 클라우드 프로그래밍 · 오승연(M20261508) 프로젝트 명세 기반 레퍼런스 데모.

---

## 1. 무엇을 할 수 있나요

1. **CSV 업로드** → 학생 전체 기록을 표로 보고, 응답자 수·평균 타수를 한눈에 확인
2. **학생 선택** → 1·2·3회차 변화 꺾은선 그래프 (학급 평균과 함께 비교)
3. **상승률 버튼** → 학급 전체 성장 퍼센티지를 순위·색상으로 요약

---

## 2. 입력 CSV 형식

| 컬럼명 | 타입 | 예시 | 필수 |
|--------|------|------|------|
| `이름` | 문자열 | 김민준 | ✅ |
| `1회차` | 정수 | 120 | ✅ |
| `2회차` | 정수 | 145 | ✅ |
| `3회차` | 정수 | 180 | ✅ |

- 인코딩: **UTF-8 / CP949(엑셀 기본) 둘 다 자동 인식**
- 1회차에 0이나 음수가 있으면 성장률 계산이 불가하므로 거부됩니다.
- 샘플 파일: 저장소에 포함된 [`sample_data.csv`](sample_data.csv) (28명)

---

## 3. 로컬에서 실행하기

```bash
# 1) 가상환경 만들기 (선택)
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 2) 라이브러리 설치
pip install -r requirements.txt

# 3) 앱 실행
streamlit run app.py
```

브라우저가 자동으로 `http://localhost:8501`을 엽니다. 사이드바에서 `sample_data.csv`를 업로드해보세요.

---

## 4. Streamlit Community Cloud 배포

1. 이 폴더를 GitHub **public 저장소**에 푸시합니다.
2. <https://share.streamlit.io> 접속 → "New app" → 저장소·브랜치·`app.py` 경로 입력.
3. Deploy 클릭 → 1~2분 후 공개 URL 생성.

> 🚨 실제 학생 이름이 든 CSV는 **절대 저장소에 올리지 마세요.** `.gitignore`가 `sample_data.csv`만 예외로 두고 나머지 `.csv`를 모두 차단합니다.

---

## 5. 개인정보 / 보안 점검

- [x] 샘플 데이터에 실제 학생 이름·정보 없음
- [x] API 키·비밀번호를 `app.py`에 직접 쓰지 않음
- [x] 공개 리포(Public)여도 무방한 데이터만 사용
- [x] `.gitignore`에 민감 파일 포함

---

## 6. 만들지 않은 것 (Out of Scope)

- 로그인/회원가입
- 데이터 영구 저장 (DB, 서버 파일)
- 외부 AI API 호출
- 이메일 발송, 알림
- 모바일 반응형 디자인 (PC 크롬 브라우저 기준)

> v2에서 추가하고 싶다면: 학생별 누적 회차 저장(SQLite), 학반 단위 비교, 학부모 PDF 리포트 등이 자연스러운 확장 방향입니다.

---

## 7. 코드 구조

```
typing_growth_tracker/
├── app.py              # Streamlit 앱 본체 (≈140 lines)
├── requirements.txt    # 의존 라이브러리 3개
├── .gitignore          # 실제 데이터 차단
├── README.md           # 이 파일
├── PROMPT_LOG.md       # Copilot에게 작성한 프롬프트 기록
└── sample_data.csv     # 더미 학생 28명
```

---

## 8. 라이선스 / 출처

수업 자료 용도의 데모 코드입니다. 자유롭게 변형해 사용하세요.
