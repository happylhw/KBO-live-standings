import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="KBO LIVE STANDINGS",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ KBO LIVE STANDINGS")
st.caption("KBO 순위 시뮬레이터")

teams = [
    "LG", "한화", "삼성", "롯데", "KIA",
    "SSG", "KT", "두산", "NC", "키움"
]

st.header("1. 현재 정규시즌 성적 입력")
st.info("각 팀의 현재 승리와 패배 횟수를 입력하세요.")

records = {}

for i in range(0, 10, 2):
    col1, col2 = st.columns(2)

    for col, team in zip([col1, col2], teams[i:i+2]):
        with col:
            st.subheader(team)
            wins = st.number_input(
                f"{team} 승",
                min_value=0,
                value=0,
                key=f"{team}_w"
            )
            losses = st.number_input(
                f"{team} 패",
                min_value=0,
                value=0,
                key=f"{team}_l"
            )
            records[team] = [wins, losses]

st.divider()

st.header("2. 현재 경기 상황 입력")

winning = st.multiselect(
    "🟢 이기고 있는 팀",
    teams
)

losing = st.multiselect(
    "🔴 지고 있는 팀",
    teams
)

drawing = st.multiselect(
    "🟡 비기고 있는 팀",
    teams
)

st.divider()

if st.button("🔥 예상 순위 계산하기", use_container_width=True):

    if set(winning) & set(losing):
        st.error("한 팀을 승리와 패배에 동시에 선택할 수 없습니다.")

    elif set(winning) & set(drawing) or set(losing) & set(drawing):
        st.error("한 팀을 여러 경기 상황에 동시에 선택할 수 없습니다.")

    else:
        result = {}

        for team, record in records.items():
            w, l = record.copy()

            if team in winning:
                w += 1

            if team in losing:
                l += 1

            rate = w / (w + l) if w + l > 0 else 0

            result[team] = {
                "팀": team,
                "승": w,
                "패": l,
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

        df["승률"] = df["승률"].map(lambda x: f"{x:.3f}")
        df["게임차"] = df["게임차"].map(lambda x: f"{x:.1f}")

        st.header("🏆 예상 최종 순위")
        st.dataframe(
            df,
            use_container_width=True
        )

        st.success("순위 계산 완료!")
