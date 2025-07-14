import streamlit as st
import pandas as pd
from progress import load_progress, add_xp

def main():
    st.title("📊 Productivity Dashboard")

    # Inputs for new session
    duration = st.number_input("Session duration (minutes):", min_value=1, step=1)
    category = st.selectbox("Category:", ["Focus", "Distraction"])
    note = st.text_input("Add a note (optional):")

    if st.button("Add XP"):
        add_xp(duration, category, note)
        st.success(f"Logged {duration} min in '{category}'.")
        st.experimental_rerun()  # Auto-refresh the app

    progress = load_progress()
    history = progress.get("history", {})

    if not history:
        st.write("No data yet. Log a session!")
        return

    # Build a DataFrame of all sessions
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

    # Total XP per day for performance trends
    daily_xp = df.groupby("date")["xp"].sum().reset_index()
    daily_xp = daily_xp.sort_values("date")

    # Calculate rolling averages
    daily_xp["7_day_avg"] = daily_xp["xp"].rolling(window=7).mean()
    daily_xp["30_day_avg"] = daily_xp["xp"].rolling(window=30).mean()

    st.subheader("XP Over Time")
    st.line_chart(daily_xp.set_index("date")[["xp", "7_day_avg", "30_day_avg"]])

    # Category breakdown chart
    category_totals = df.groupby("category")["xp"].sum()
    st.subheader("XP by Category")
    st.bar_chart(category_totals)

    # Display session notes
    st.subheader("Session Notes")
    for idx, row in df.sort_values("date", ascending=False).iterrows():
        with st.expander(f"{row['date'].date()} - {row['category']} ({row['xp']} XP)"):
            st.write(row["note"] if row["note"] else "*No note added*")

    # Show total XP and streak
    st.write(f"**Total XP:** {progress.get('xp', 0)}")
    st.write(f"**Current Streak:** {progress.get('streak', 0)} day(s)")

if __name__ == "__main__":
    main()
