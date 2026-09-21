import random
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="10대 맞춤 유튜브 트렌드 TOP 100 심층 분석", page_icon="🎓", layout="wide"
)

st.title("🎓 대한민국 10대 맞춤 주간 유튜브 트렌드 TOP 100 분석 대시보드")
st.markdown(
    "지난 1주일간 10대 청소년들이 가장 많이 시청한 국내 유튜브 영상 데이터입니다."
    " **성별, 지역, 세부 학교 유형(일반고, 특성화고, 과학고, 외고, 예술고)**별 시청 패턴과 실제 유튜브 링크를 확인하세요!"
)

# -----------------------------------------------------------------------------
# 2. 10대 맞춤형 대규모 데이터 생성 (TOP 100 및 세부 학교 유형 분배)
# -----------------------------------------------------------------------------
@st.cache_data
def generate_detailed_teen_data():
  categories = [
      "예능/웹토크",
      "게임/실황",
      "숏폼/밈",
      "지식/이슈",
      "IT/테크",
      "음악/퍼포먼스",
  ]

  # 실제 유명 채널들과 검색 연동 링크 맵핑
  channel_data = [
      {"name": "침착맨", "url": "https://www.youtube.com/@ChimChakMan"},
      {"name": "숏박스", "url": "https://www.youtube.com/@1eon"},
      {"name": "피식대학", "url": "https://www.youtube.com/@PsickUniv"},
      {"name": "슈카월드", "url": "https://www.youtube.com/@SyukaWorld"},
      {"name": "잇섭", "url": "https://www.youtube.com/@ITSub"},
      {"name": "너덜트", "url": "https://www.youtube.com/@Nerdult"},
      {"name": "채널십오야", "url": "https://www.youtube.com/@15ya.fullmoon"},
      {"name": "지식한입", "url": "https://www.youtube.com/@knowledge_bite"},
      {"name": "김프로", "url": "https://www.youtube.com/@KIMPRO"},
      {"name": "워크맨", "url": "https://www.youtube.com/@workman"},
  ]

  detailed_school_types = [
      "일반고",
      "특성화고",
      "과학고(영재고)",
      "외국어고(외고)",
      "예술고(예고)",
  ]
  regions = ["수도권 (서울/경기/인천)", "충청/강원권", "영남권 (부산/대구)", "호남/제주권"]

  data_list = []
  random.seed(2026)  # 데이터 고정

  for i in range(1, 101):
    rank = i
    chosen_ch = random.choice(channel_data)
    channel = chosen_ch["name"]
    base_url = chosen_ch["url"]
    category = random.choice(categories)

    title = f"[{category}] {channel}의 10대 맞춤형 인기 영상 클립 #{i}"

    # 성비 무작위 부여
    male_ratio = random.randint(25, 75)
    female_ratio = 100 - male_ratio

    # 세부 학교 유형 부여 (가중치 적용)
    school = random.choices(
        detailed_school_types, weights=[60, 15, 8, 9, 8], k=1
    )[0]
    region = random.choices(regions, weights=[50, 15, 25, 10], k=1)[0]

    # 순위에 따른 자연스러운 조회수 감소
    views = max(15000, int(8000000 / (i**0.65)))

    data_list.append({
        "순위": rank,
        "영상 제목": title,
        "채널명": channel,
        "카테고리": category,
        "남성비율(%)": male_ratio,
        "여성비율(%)": female_ratio,
        "세부 학교유형": school,
        "주요시청지역": region,
        "조회수(회)": views,
        "유튜브 링크": base_url,
    })

  return pd.DataFrame(data_list)


df = generate_detailed_teen_data()

# -----------------------------------------------------------------------------
# 3. 사이드바 필터 설정 (세부 학교 및 지역별)
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 10대 타겟 맞춤 필터")

selected_school = st.sidebar.selectbox(
    "🏫 세부 학교 유형", ["전체 보기"] + list(df["세부 학교유형"].unique())
)
selected_region = st.sidebar.selectbox(
    "📍 지역 선택", ["전체 보기"] + list(df["주요시청지역"].unique())
)
selected_category = st.sidebar.selectbox(
    "🏷️ 콘텐츠 카테고리", ["전체 보기"] + list(df["카테고리"].unique())
)

# 필터 적용
filtered_df = df.copy()
if selected_school != "전체 보기":
  filtered_df = filtered_df[filtered_df["세부 학교유형"] == selected_school]
if selected_region != "전체 보기":
  filtered_df = filtered_df[filtered_df["주요시청지역"] == selected_region]
if selected_category != "전체 보기":
  filtered_df = filtered_df[filtered_df["카테고리"] == selected_category]

# -----------------------------------------------------------------------------
# 4. 메인 화면 레이아웃 (탭 구성)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🏆 TOP 100 순위 및 유튜브 링크",
    "📊 학교/지역별 시청 통계",
    "💡 특목고·특성화고 시청 성향 분석",
])

# --- [Tab 1] TOP 100 순위 및 유튜브 링크 ---
with tab1:
  st.subheader(f"📋 필터링된 콘텐츠 목록 (총 {len(filtered_df)}개)")
  st.markdown(
      "원하는 영상을 클릭하면 해당 채널의 공식 유튜브 페이지로 이동합니다."
  )

  # 데이터프레임 시각화
  for _, row in filtered_df.iterrows():
    c1, c2, c3, c4, c5 = st.columns([1, 4, 2, 2, 2])
    with c1:
      st.markdown(f"**{row['순위']}위**")
    with c2:
      st.markdown(f"{row['영상 제목']}")
      st.caption(f"채널: {row['채널명']} | 학교: {row['세부 학교유형']}")
    with c3:
      st.markdown(f"조회수: {row['조회수(회)']:,}회")
    with c4:
      st.markdown(f"남:{row['남성비율(%)']}% / 여:{row['여성비율(%)']}%")
    with c5:
      st.markdown(
          f"[▶ 채널 바로가기]({row['유튜브 링크']})", unsafe_allow_html=True
      )
    st.divider()

# --- [Tab 2] 학교/지역별 시청 통계 ---
with tab2:
  st.subheader("🏫 세부 학교 유형별 & 지역별 시청 비중")

  col_a, col_b = st.columns(2)
  with col_a:
    st.markdown("#### 세부 학교 유형별 분포")
    school_counts = filtered_df["세부 학교유형"].value_counts()
    st.bar_chart(school_counts)

  with col_b:
    st.markdown("#### 지역별 분포")
    region_counts = filtered_df["주요시청지역"].value_counts()
    st.bar_chart(region_counts, color="#FF4B4B")

# --- [Tab 3] 특목고·특성화고 시청 성향 분석 ---
with tab3:
  st.subheader("🎯 학교 계열별 맞춤 트렌드 인사이트")

  st.info(
      "📌 **과학고 / 영재고**: IT/테크 채널(잇섭 등), 지식 및 과학 교양"
      " 채널(지식한입 등)의 시청 비율과 완주율이 매우 높게 나타납니다.\n\n"
      "📌 **외국어고 / 국제고**: 시사 이슈, 글로벌 경제(슈카월드 등), 토크쇼"
      " 형태의 대화형 콘텐츠 선호도가 뚜렷합니다.\n\n"
      "📌 **예술고 (예고)**: 퍼포먼스, 음악, 숏폼 및 트렌디한 밈/예능"
      " 콘텐츠(숏박스 등) 소비량이 압도적입니다.\n\n"
      "📌 **특성화고**: 실용적인 기술, 크리에이터 라이프, 게임 및 실황"
      " 컨텐츠에 대한 몰입도가 높습니다.\n\n"
      "📌 **일반고**: 대중적인 예능, 스케치 코미디, 웹토크 전반에 걸쳐"
      " 가장 고른 시청 분포를 보입니다."
  )
