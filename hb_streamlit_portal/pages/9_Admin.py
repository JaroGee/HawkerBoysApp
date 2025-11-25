from __future__ import annotations

from datetime import date

import streamlit as st

from core.gamification import complete_task_with_approval
from core.models import Mission, MissionTask
from core.storage import get_storage


TRACKS = ["kitchen", "stall_ops", "life_mindset"]


def guard_admin() -> bool:
    if not st.session_state.get("is_admin"):
        st.error("Admin password required. Set it in the sidebar.")
        return False
    return True


def render_trainee_overview(storage) -> None:
    st.subheader("Trainees")
    trainees = storage.list_trainees()
    table = [
        {
            "Name": t.name,
            "Cohort": t.cohort or "-",
            "Stage": t.current_stage,
            "Overall XP": t.overall_xp,
        }
        for t in trainees
    ]
    st.table(table)


def render_pending_tasks(storage) -> None:
    st.subheader("Approvals")
    trainees = storage.list_trainees()
    trainee_lookup = {t.name: t for t in trainees}
    selected = st.selectbox("Select trainee", list(trainee_lookup.keys())) if trainees else None
    if not selected:
        st.info("No trainees available.")
        return
    trainee = trainee_lookup[selected]
    progress = storage.list_task_progress_for_trainee(trainee.id)
    pending = [p for p in progress if p.status == "pending_approval"]
    if not pending:
        st.info("No tasks awaiting approval.")
        return
    for item in pending:
        task = storage.get_task(item.task_id)
        mission = storage.get_mission(task.mission_id) if task else None
        cols = st.columns([3, 2, 1])
        with cols[0]:
            st.write(f"{task.title if task else 'Task'}")
            if mission:
                st.caption(f"Mission: {mission.title}")
        with cols[1]:
            st.write(task.track if task else "-")
        with cols[2]:
            if st.button("Approve", key=f"approve-{item.task_id}") and task:
                complete_task_with_approval(storage, trainee, task, approver="admin")
                st.success("Task approved")


def render_mission_builder(storage) -> None:
    st.subheader("Create mission")
    with st.form("create-mission"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        stage = st.selectbox("Stage", ["Orientation", "Skills Training", "Stall Practice", "Placement", "Ownership Pathway"])
        active_from = st.date_input("Active from", value=date.today())
        total_xp_reward = st.number_input("Total XP", min_value=0, value=100, step=10)
        submitted = st.form_submit_button("Add mission")
        if submitted:
            mission = Mission(
                id=f"mission-{len(storage.missions)+1}",
                title=title,
                description=description,
                stage=stage,
                active_from=active_from,
                total_xp_reward=total_xp_reward,
            )
            storage.save_mission(mission)
            st.success("Mission added")

    st.subheader("Add task to mission")
    mission_choices = {m.title: m.id for m in storage.missions.values()}
    if not mission_choices:
        st.info("Create a mission first.")
        return
    with st.form("create-task"):
        mission_title = st.selectbox("Mission", list(mission_choices.keys()))
        title = st.text_input("Task title")
        description = st.text_area("Task description")
        track = st.selectbox("Track", TRACKS)
        xp_reward = st.number_input("XP", min_value=10, max_value=300, value=40, step=10)
        auto_complete = st.checkbox("Allow trainee to self-complete", value=True)
        submitted = st.form_submit_button("Add task")
        if submitted:
            task = MissionTask(
                id=f"task-{len(storage.tasks)+1}",
                mission_id=mission_choices[mission_title],
                title=title,
                description=description,
                track=track,
                xp_reward=xp_reward,
                auto_complete=auto_complete,
            )
            storage.save_task(task)
            st.success("Task added")


def render_support_requests(storage) -> None:
    st.subheader("Support requests")
    requests = storage.list_support_requests()
    if not requests:
        st.info("No support requests yet.")
        return
    for req in requests:
        cols = st.columns([3, 2, 1])
        with cols[0]:
            trainee = storage.get_trainee(req.trainee_id)
            st.write(f"{trainee.name if trainee else req.trainee_id}")
            st.caption(req.message)
        with cols[1]:
            st.write(req.category)
        with cols[2]:
            new_status = st.selectbox(
                "Status", ["new", "in_progress", "handled"], index=["new", "in_progress", "handled"].index(req.status), key=f"status-{req.id}"
            )
            if new_status != req.status:
                req.status = new_status
                storage.save_support_request(req)
                st.success("Updated")


def main() -> None:
    st.title("Admin")
    storage = get_storage()
    if not guard_admin():
        return
    render_trainee_overview(storage)
    st.divider()
    render_pending_tasks(storage)
    st.divider()
    render_mission_builder(storage)
    st.divider()
    render_support_requests(storage)


if __name__ == "__main__":
    main()
