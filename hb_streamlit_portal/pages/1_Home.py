from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from core.storage import get_storage

STAGES = ["Orientation", "Skills Training", "Stall Practice", "Placement", "Ownership Pathway"]


def render_stage_progress(current_stage: str) -> None:
    st.subheader("Journey to Stall Ownership")
    cols = st.columns(len(STAGES))
    for idx, stage in enumerate(STAGES):
        with cols[idx]:
            active = stage == current_stage
            color = "#f76b1c" if active else "#1f2933"
            st.markdown(
                f"""
                <div style='padding:0.6rem;border-radius:8px;background:{color};color:#f3f4f6;text-align:center;'>
                    {stage}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_focus(storage, trainee_id: str) -> None:
    st.subheader("This week's focus")
    missions = storage.list_missions_for_trainee(trainee_id)
    suggestions = []
    progress_lookup = {p.task_id: p for p in storage.list_task_progress_for_trainee(trainee_id)}
    for mission in missions:
        for task in storage.list_tasks_for_mission(mission.id):
            prog = progress_lookup.get(task.id)
            if not prog or prog.status == "not_started":
                suggestions.append((mission.title, task.title, task.track, task.xp_reward))
    if suggestions:
        for mission_title, task_title, track, xp in suggestions[:3]:
            st.markdown(f"- **{task_title}** in _{mission_title}_ ({track}, {xp} XP)")
    else:
        st.info("You are on top of your tasks. Great work!")


def render_summary(storage, trainee_id: str) -> None:
    st.subheader("Recent progress")
    completed = [
        p
        for p in storage.list_task_progress_for_trainee(trainee_id)
        if p.status == "completed" and p.completed_at
    ]
    recent = [p for p in completed if p.completed_at and p.completed_at >= datetime.utcnow() - timedelta(days=7)]
    mission_progress = storage.list_mission_progress_for_trainee(trainee_id)
    completed_missions = [m for m in mission_progress if m.status == "completed"]
    st.write(
        f"You completed **{len(recent)} tasks** and **{len(completed_missions)} missions** in the last 7 days."
    )


def main() -> None:
    st.title("Home")
    storage = get_storage()
    trainee_id = st.session_state.get("trainee_id")
    if not trainee_id:
        st.info("Select your trainee profile from the sidebar to see your journey.")
        return
    trainee = storage.get_trainee(trainee_id)
    if not trainee:
        st.error("Trainee not found.")
        return

    render_stage_progress(trainee.current_stage)
    st.divider()
    render_focus(storage, trainee_id)
    st.divider()
    render_summary(storage, trainee_id)


if __name__ == "__main__":
    main()
