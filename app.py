import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(
    page_title="KBO LIVE STANDINGS",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ KBO LIVE STANDINGS")
st.caption("KBO 공식 기록 기반 순위 시뮬레이터")

TEAMS = [
    "LG", "한화", "삼성", "롯데", "KIA",
    "SSG", "KT", "두산", "NC", "키움"
]

KBO_URL = (
    "https://www.koreabaseball.com/"
    "Record/TeamRank/TeamRank.aspx"
)


@st.cache_data(ttl=300)
def load_standings():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        KBO_URL,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    tables = pd.read_html(
        StringIO(response.text),
        flavor="lxml"
    )

    for table in tables:

        df = table.copy()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                "".join(str(x) for x in col)
                for col in df.columns
            ]

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        required = ["팀명", "승", "패", "무"]

        if not all(c in df.columns for c in required):
            continue

        df = df[required].copy()

        df["팀명"] = df["팀명"].astype(str).str.strip()

        df = df[df["팀명"].isin(TEAMS)]

        for col in ["승", "패", "무"]:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = df.dropna()

        if len(df) == 10:
            return df

    raise ValueError("KBO 순위표를 찾지 못했습니다.")


try:
    standings = load_standings()

    st.success("KBO 공식 순위를 불러왔습니다.")

    st.subheader("📊 현재 정규시즌 순위")

    st.dataframe(
        standings,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:

    st.error(
        "KBO 순위 데이터를 불러오지 못했습니다."
    )

    st.caption(str(e))
    st.stop()


st.divider()

st.header("⚾ 경기 상황 입력")

st.info(
    "현재 진행 중인 경기의 상황을 선택하세요."
)

winning = st.multiselect(
    "🟢 이기고 있는 팀",
    TEAMS
)

losing = st.multiselect(
    "🔴 지고 있는 팀",
    TEAMS
)

drawing = st.multiselect(
    "🟡 비기고 있는 팀",
    TEAMS
)


st.divider()

if st.button(
    "🔥 예상 순위 계산하기",
    use_container_width=True
):

    if (
        set(winning) & set(losing)
        or set(winning) & set(drawing)
        or set(losing) & set(drawing)
    ):

        st.error(
            "한 팀을 여러 경기 상황에 동시에 선택할 수 없습니다."
        )

    else:

        result = {}

        for _, row in standings.iterrows():

            team = row["팀명"]

            w = int(row["승"])
            l = int(row["패"])
            d = int(row["무"])

            if team in winning:
                w += 1

            if team in losing:
                l += 1

            rate = (
                w / (w + l)
                if w + l > 0
                else 0
            )

            result[team] = {
                "팀": team,
                "승": w,
                "패": l,
                "무": d,
                "승률": rate
            }

        ranking = sorted(
            result.values(),
            key=lambda x: x["승률"],
            reverse=True
        )

        top = ranking[0]

        for team in ranking:

            team["게임차"] = (
                (top["승"] - team["승"])
                + (team["패"] - top["패"])
            ) / 2

        df = pd.DataFrame(ranking)

        df.index = range(1, 11)
        df.index.name = "순위"

        df["승률"] = df["승률"].map(
            lambda x: f"{x:.3f}"
        )

        df["게임차"] = df["게임차"].map(
            lambda x: f"{x:.1f}"
        )

        st.header("🏆 예상 순위")

        st.dataframe(
            df,
            use_container_width=True
        )

        st.success("예상 순위 계산 완료!")
