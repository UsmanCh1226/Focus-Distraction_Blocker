import streamlit as st
import pandas as pd
from progress import load_progress, add_xp
import calplot
import matplotlib.pyplot as plt


CATEGORY_COLORS = {
    "Focus": "🟢",
    "Distraction": "🔴"
}

def main():
    st.set_page_config(page_title="Focus Tracker", layout="wide")
    st.markdown(
        "<h1 style='color:#4CAF50;'>🌟 Focus & XP Tracker Dashboard</h1>",
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.header("🎛️ Customize")
        theme = st.selectbox("Choose Theme:", ["Light", "Dark"])
        if theme == "Dark":
            st.markdown(
                """
                <style>
                    .main { background-color: #0e1117; color: #f0f0f0; }
                    .css-1aumxhk, .css-ffhzg2 { background-color: #0e1117 !important; color: #f0f0f0 !important; }
                </style>
                """,
                unsafe_allow_html=True
            )

    st.markdown("## 🎯 Log a Focus Session")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        duration = st.number_input("⏱ Duration (minutes):", min_value=1, step=1)
    with col2:
        category = st.selectbox("📂 Category:", list(CATEGORY_COLORS.keys()))
    with col3:
        note = st.text_input("📝 Note (optional):")

    if st.button("✅ Add XP"):
        add_xp(duration, category, note)
        st.success(f"Logged {duration} min in {CATEGORY_COLORS[category]} '{category}'")
        st.experimental_rerun()

    progress = load_progress()
    history = progress.get("history", {})

    if not history:
        st.info("No data yet. Log a session to get started!")
        return

    sessions = []
    for day, entries in history.items():
        for e in entries:
            sessions.append({
                "date": pd.to_datetime(day),
                "xp": e["xp"],
                "category": e["category"],
                "note": e["note"]
            })

    df = pd.DataFrame(sessions)

    st.markdown("## 📈 XP Performance Trends")
    daily_xp = df.groupby("date")["xp"].sum().reset_index().sort_values("date")
    daily_xp["7_day_avg"] = daily_xp["xp"].rolling(window=7).mean()
    daily_xp["30_day_avg"] = daily_xp["xp"].rolling(window=30).mean()

    st.line_chart(daily_xp.set_index("date")[["xp", "7_day_avg", "30_day_avg"]])

    st.markdown("## 🧩 XP by Category")
    category_totals = df.groupby("category")["xp"].sum()
    st.bar_chart(category_totals)

    st.markdown("## 📓 Session History with Notes")
    for idx, row in df.sort_values("date", ascending=False).iterrows():
        with st.expander(f"{row['date'].date()} — {CATEGORY_COLORS[row['category']]} {row['category']} ({row['xp']} XP)"):
            st.write(row["note"] if row["note"] else "*No note added*")

    st.markdown("## 📅 Daily XP Heatmap")

    xp_by_day = df.groupby(df["date"].dt.date)["xp"].sum()

    # Convert to a Pandas Series with datetime index
    xp_series = pd.Series(xp_by_day.values, index=pd.to_datetime(xp_by_day.index))

    fig, ax = calplot.calplot(
        xp_series,
        cmap="YlGn",  # Yellow-Green gradient
        suptitle="Daily XP Activity",
        colorbar=True,
        how='sum',
        figsize=(10, 3),
    )

    st.pyplot(fig)

    st.markdown("## 🔢 Overall Stats")
    st.write(f"**🌟 Total XP:** `{progress.get('xp', 0)}`")
    st.write(f"**🔥 Current Streak:** `{progress.get('streak', 0)} day(s)`")

if __name__ == "__main__":
    main()
