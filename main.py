from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 스트림릿 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 박스오피스 심층 분석", page_icon="🍿", layout="wide"
)

st.title("🍿 KOBIS 박스오피스 인사이트 & 심층 분석")
st.markdown(
    "영화진흥위원회(KOBIS) Open API를 활용하여 한국 시간 기준 **어제**의 박스오피스 순위와 흥행 지표를 분석합니다."
)

# -----------------------------------------------------------------------------
# 2. KOBIS 인증키 불러오기 (비밀 금고 Secrets 활용)
# -----------------------------------------------------------------------------
try:
  api_key = st.secrets["KOBIS_KEY"]
except Exception:
  st.error(
    "⚠️ 스트림릿 비밀 금고(Secrets)에 `KOBIS_KEY`가 설정되어 있지 않습니다."
  )
  st.info(
    "💡 **해결 방법**: Streamlit Cloud 앱 설정(Settings -> Secrets) 또는 로컬의"
    " `.streamlit/secrets.toml` 파일에 `KOBIS_KEY = '발급받은키'` 형태로"
    " 추가해주세요."
  )
  st.stop()

# -----------------------------------------------------------------------------
# 3. 한국 시간(KST) 기준 '어제' 날짜 자동 계산 (YYYYMMDD 형식)
# -----------------------------------------------------------------------------
kst = timezone(timedelta(hours=9))  # 한국 표준시(UTC+9)
yesterday = datetime.now(kst) - timedelta(days=1)
target_dt = yesterday.strftime("%Y%m%d")

st.subheader(f"📅 조회 기준일: {yesterday.strftime('%Y년 %m월 %d일')}")


# -----------------------------------------------------------------------------
# 4. KOBIS API 데이터 호출 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_box_office(key, target_date):
  url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
  params = {"key": key, "targetDt": target_date}

  try:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
  except requests.exceptions.RequestException as e:
    return {"error": f"네트워크 요청 실패: {e}"}


with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
  result = fetch_box_office(api_key, target_dt)

# -----------------------------------------------------------------------------
# 5. 오류 및 예외 상황 처리 (사용자 안내)
# -----------------------------------------------------------------------------
if "error" in result:
  st.error(f"❌ 오류가 발생했습니다: {result['error']}")
  st.info(
    "💡 **확인해 주세요**: 인터넷 연결 상태나 방화벽 설정을 확인하시고, 잠시 후"
    " 다시 시도해 주세요."
  )
  st.stop()

if "faultInfo" in result:
  st.error(f"❌ KOBIS API 인증/요청 오류: {result['faultInfo']}")
  st.info(
    "💡 **확인해 주세요**: Streamlit Secrets에 등록된 `KOBIS_KEY` 값이 정확한지 확인해"
    " 주세요."
  )
  st.stop()

box_office_result = result.get("boxOfficeResult", {})
movie_list = box_office_result.get("dailyBoxOfficeList", [])

if not movie_list:
  st.warning(
    "⚠️ 조회된 영화 데이터가 없습니다. (아직 집계가 완료되지 않았거나 해당"
    " 날짜의 데이터가 없을 수 있습니다.)"
  )
  st.info(
    "💡 **확인해 주세요**: 영화진흥위원회 서버에 어제 날짜의 박스오피스 데이터가"
    " 정상적으로 업데이트되었는지 확인해 주세요."
  )
  st.stop()

# -----------------------------------------------------------------------------
# 6. 데이터프레임 가공 및 정제 (다양한 지표 추가)
# -----------------------------------------------------------------------------
df = pd.DataFrame(movie_list)

# 순위 증감 가공 (예: 양수면 '▲', 음수면 '▼', 0이면 '-')
def format_rank_inten(val):
  v = int(val)
  if v > 0:
    return f"▲ {v}"
  elif v < 0:
    return f"▼ {abs(v)}"
  else:
    return "-"

df["순위증감"] = df["rankInten"].apply(format_rank_inten)
df["신작여부"] = df["rankOldAndNew"].apply(
    lambda x: "✨ 신작" if x == "NEW" else "기존"
)

# 시각화 및 표를 위한 정제된 데이터프레임
df_display = df[[
    "rank",
    "순위증감",
    "movieNm",
    "openDt",
    "audiCnt",
    "audiAcc",
    "salesShare",
    "scrnCnt",
    "신작여부",
]].copy()

df_display.columns = [
    "순위",
    "전일증감",
    "영화명",
    "개봉일",
    "관객수(명)",
    "누적관객(명)",
    "매출점유율(%)",
    "스크린수",
    "구분",
]

# 숫자형으로 변환
df_display["관객수(명)"] = pd.to_numeric(df_display["관객수(명)"])
df_display["누적관객(명)"] = pd.to_numeric(df_display["누적관객(명)"])
df_display["매출점유율(%)"] = pd.to_numeric(df_display["매출점유율(%)"])
df_display["스크린수"] = pd.to_numeric(df_display["스크린수"])

# -----------------------------------------------------------------------------
# 7. 탭(Tab) 메뉴 구성으로 깔끔한 화면 분리
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🏆 1위 집중 분석",
    "📊 관객수 & 점유율 비교",
    "📋 전체 순위표 및 상세",
])

# --- [Tab 1] 1위 집중 분석 ---
with tab1:
  top_movie = movie_list[0]
  st.markdown(f"### 👑 어제의 박스오피스 1위: **{top_movie['movieNm']}**")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(
        label="🎫 어제 관객수",
        value=f"{int(top_movie['audiCnt']):,}명",
        delta=f"순위 변동: {format_rank_inten(top_movie['rankInten'])}",
    )
  with col2:
    st.metric(
        label="📈 누적 관객수", value=f"{int(top_movie['audiAcc']):,}명"
    )
  with col3:
    st.metric(
        label="💰 전체 박스오피스 매출 점유율",
        value=f"{top_movie['salesShare']}%",
    )

  st.info(
      f"💡 **1위 영화 소식**: {top_movie['movieNm']}은(는) {top_movie['openDt']}에"
      f" 개봉하였으며, 어제 하루 동안 총 **{int(top_movie['scrnCnt']):,}개**의"
      " 스크린에서 상영되었습니다."
  )

# --- [Tab 2] 관객수 & 점유율 비교 ---
with tab2:
  st.markdown("### 📊 관객수 상위 5편 영화 비교")
  top_5_df = df_display.head(5).set_index("영화명")[["관객수(명)"]]
  st.bar_chart(top_5_df)

  st.markdown("### 🥧 박스오피스 매출 점유율 Top 5")
  top_5_share = df_display.head(5).set_index("영화명")[["매출점유율(%)"]]
  st.bar_chart(top_5_share, color="#FF4B4B")

# --- [Tab 3] 전체 순위표 및 상세 ---
with tab3:
  st.markdown("### 📋 전체 박스오피스 상세 순위")
  st.dataframe(df_display, use_container_width=True, hide_index=True)
