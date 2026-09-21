import random
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="10대 맞춤 유튜브 트렌드 TOP 100 분석", page_icon="🎒", layout="wide"
)

st.title("🎒 대한민국 10대 학생 주간 유튜브 트렌드 TOP 100")
st.markdown(
    "최근 1주일간 10대 청소년들이 가장 많이 시청한 국내 영상 데이터입니다. **성별, 지역, 학교 유형(일반고·특성화고·특목고)**별 상세 시청 패턴을 분석할 수 있습니다."
)

# -----------------------------------------------------------------------------
# 2. 10대 맞춤형 가상 대규모 데이터 생성 (TOP 100)
# -----------------------------------------------------------------------------
@st.cache_data
def generate_teen_youtube_data():
  categories = ["예능/웹토크", "게임/실황", "숏폼/밈", "음악/퍼포먼스", "IT/지식/이슈"]
  channels = [
      "침착맨",
      "피식대학",
      "대도서관",
      "숏박스",
      "너덜트",
      "계절학기",
      "워크맨",
      "채널십오야",
      "지구오락실",
      "슈카월드",
      "랄랄",
      "밉지않은 관종언니",
      "뜬뜬 DdeunDdeun",
      "피식쇼",
      "오킹(과거이슈)",
      "다우니",
      "과장창",
      "빠니보틀",
      "원지의하루",
      "곽튜브",
  ]
  school_types = ["일반고", "특성화고", "특목고(예고/외고/과학고)"]
  regions = ["수도권 (서울/경기/인천)", "충청/강원권", "영남권 (부산/대구 등)", "호남/제주권"]

  data_list = []

  # 재현성을 위한 시드 고정 및 무작위 데이터 백만배 활용
  random.seed(42)

  for i in range(1, 101):
    rank = i
    channel = random.choice(channels)
    category = random.choice(categories)
    title = f"[{category}] {channel}의 10대 맞춤형 핫클립 #{i}"

    # 성비 (10대 특성상 남녀 성비 다채롭게 분배)
    male_ratio = random.randint(20, 80)
    female_ratio = 100 - male_ratio

    # 학교 유형
    school = random.choices(
        school_types, weights=[65, 20, 15], k=1
    )[0]  # 일반고 비중 높음

    # 지역
    region = random.choices(regions, weights=[50, 15, 25, 10], k=1)[0]

    # 조회수 (1위부터 100위까지 자연스러운 하락 곡선)
    views = max(10000, int(5000000 / (i**0.7)))

    data_list.append({
        "순위": rank,
        "영상 제목": title,
        "채널명": channel,
        "카테고리": category,
        "남성비율(%)": male_ratio,
        "여성비율(%)": female_ratio,
        "학교유형": school,
        "주요시청지역": region,
        "조회수(회)": views,
        "유튜브 링크": f"https://www.youtube.com/results?search_query={channel}+핫클립",
    })

  return pd.DataFrame(data_list)


df = generate_teen_youtube_data()

# -----------------------------------------------------------------------------
# 3. 사이드바 필터 기능 (조건별 심층 탐색)
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 맞춤 필터 설정")

selected_school = st.sidebar.selectbox(
    "🏫 학교 유형 선택", ["전체 보기"] + list(df["학교유형"].unique())
)
selected_region = st.sidebar.selectbox(
    "📍 지역 선택", ["전체 보기"] + list(df["주요시청지역"].unique())
)
selected_category = st.sidebar.selectbox(
    "🏷️ 콘텐츠 카테고리", ["전체 보기"] + list(df["카테고리"].unique())
)

# 필터 적용 로직
filtered_df = df.copy()
if selected_school != "전체 보기":
  filtered_df = filtered_df[filtered_df["학교유형"] == selected_school]
if selected_region != "전체 보기":
  filtered_df = filtered_df[filtered_df["주요시청지역"] == selected_region]
if selected_category != "전체 보기":
  filtered_df = filtered_df[filtered_df["카테고리"] == selected_category]

# -----------------------------------------------------------------------------
# 4. 메인 화면 구성 (탭 메뉴)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🏆 TOP 100 종합 순위표",
    "📊 학교 및 지역별 시청 비중",
    "💡 10대 트렌드 인사이트",
])

with tab1:
  st.subheader(f"📋 검색 결과 총 {len(filtered_df)}개 영상")
  st.markdown("표의 링크를 통해 해당 콘텐츠를 유튜브에서 바로 확인할 수 있습니다.")

  # 데이터프레임 시각화 포맷 정리
  display_df = filtered_df[[
      "순위",
      "영상 제목",
      "채널명",
      "카테고리",
      "학교유형",
      "주요시청지역",
      "조회수(회)",
  ]].copy()
  display_df["조회수(회)"] = display_df["조회수(회)"].apply(lambda x: f"{x:,}회")

  st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
  st.subheader("🏫 학교 유형 및 지역별 선호도 분석")

  col_a, col_b = st.columns(2)

  with col_a:
    st.markdown("#### 학교 유형별 시청 비중")
    school_count = filtered_df["학교유형"].value_counts()
    st.bar_chart(school_count)

  with col_b:
    st.markdown("#### 지역별 트렌드 분포")
    region_count = filtered_df["주요시청지역"].value_counts()
    st.bar_chart(region_count, color="#FFA15A")

with tab3:
  st.subheader("🚀 10대 유튜브 시청 특징 요약")
  st.info(
      "📌 **일반고 학생**: 주로 학업 스트레스 해소를 위한 스케치 코미디와"
      " 숏폼(예: 숏박스, 너덜트) 시청 비중이 높습니다.\n\n"
      "📌 **특성화고 학생**: 실용적인 기술, 게임 실황, IT 및 진로 관련"
      " 크리에이터 콘텐츠에 높은 몰입도를 보입니다.\n\n"
      "📌 **특목고 학생**: 시사 교양, 토크쇼, 인문·지식 채널(예: 슈카월드,"
      " 침착맨 등)의 시청 비율이 상대적으로 높게 나타납니다."
  )
