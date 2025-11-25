from __future__ import annotations

import streamlit as st

from core.gamification import XP_THRESHOLDS, recalculate_levels
from core.storage import get_storage


def progress_bar(label: str, xp: int) -> None:
    current_level = 1
    next_threshold = XP_THRESHOLDS[-1]
    for idx, threshold in enumerate(XP_THRESHOLDS):
        if xp >= threshold:
            current_level = idx + 1
    for threshold in XP_THRESHOLDS:
        if threshold > xp:
            next_threshold = threshold
            break
    percent = min(1.0, xp / next_threshold) if next_threshold else 1.0
    st.write(f"{label} - Level {current_level}")
    st.progress(percent)
    st.caption(f"{xp} XP toward next level at {next_threshold} XP")


def main() -> None:
    st.title("Progress")
    storage = get_storage()
    trainee_id = st.session_state.get("trainee_id")
    if not trainee_id:
        st.info("Select your trainee profile from the sidebar to view progress.")
        return
    trainee = storage.get_trainee(trainee_id)
    if not trainee:
        st.error("Trainee not found.")
        return

    levels = recalculate_levels(trainee)
    st.subheader(f"Overall Level {levels.overall_level}")
    st.metric("Total XP", trainee.overall_xp)

    st.divider()
    st.subheader("Tracks")
    progress_bar("Kitchen Skills", trainee.kitchen_xp)
    progress_bar("Stall Operations", trainee.stall_ops_xp)
    progress_bar("Life & Mindset", trainee.life_mindset_xp)

    st.divider()
    st.subheader("Badges")
    earned_badges = storage.list_badges_for_trainee(trainee_id)
    badge_catalog = {b.id: b for b in storage.list_badges()}
    if not earned_badges:
        st.info("No badges earned yet. Keep going!")
    else:
        for tb in earned_badges:
            badge = badge_catalog.get(tb.badge_id)
            if badge:
                st.markdown(f"- **{badge.name}** — {badge.description} (Awarded {tb.awarded_at.date()})")

    st.divider()
    st.subheader("Cohort context")
    st.write("Most trainees in your cohort are between Level 2 and Level 5. Keep steady progress toward your goals.")


if __name__ == "__main__":
    main()
