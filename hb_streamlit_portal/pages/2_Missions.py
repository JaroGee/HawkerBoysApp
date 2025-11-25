from __future__ import annotations

import streamlit as st

from core.gamification import record_task_completion
from core.storage import get_storage


STATUS_LABELS = {
    "not_started": "Not started",
    "in_progress": "In progress",
    "completed": "Completed",
    "pending_approval": "Pending approval",
}


def render_task_row(trainee, task, progress_lookup, storage) -> None:
    progress = progress_lookup.get(task.id)
    status_label = STATUS_LABELS.get(progress.status, progress.status) if progress else "Not started"
    cols = st.columns([3, 2, 1, 2])
    with cols[0]:
        st.markdown(f"**{task.title}**")
        st.caption(task.description)
    with cols[1]:
        st.write(task.track)
    with cols[2]:
        st.write(f"{task.xp_reward} XP")
    with cols[3]:
        if task.auto_complete:
            if progress and progress.status == "completed":
                st.success("Completed")
            else:
                if st.button("Mark complete", key=f"complete-{task.id}"):
                    record_task_completion(storage, trainee, task, requires_approval=False)
                    st.success("Task marked complete")
        else:
            if progress and progress.status == "completed":
                st.success("Approved")
            elif progress and progress.status == "pending_approval":
                st.info("Pending approval")
            else:
                if st.button("Submit for review", key=f"submit-{task.id}"):
                    record_task_completion(storage, trainee, task, requires_approval=True)
                    st.info("Submitted for mentor approval.")


def main() -> None:
    st.title("Missions")
    storage = get_storage()
    trainee_id = st.session_state.get("trainee_id")
    if not trainee_id:
        st.info("Select your trainee profile from the sidebar to see missions.")
        return
    trainee = storage.get_trainee(trainee_id)
    if not trainee:
        st.error("Trainee not found.")
        return

    missions = storage.list_missions_for_trainee(trainee_id)
    task_progress = storage.list_task_progress_for_trainee(trainee_id)
    progress_lookup = {p.task_id: p for p in task_progress}

    for mission in missions:
        tasks = storage.list_tasks_for_mission(mission.id)
        completed = sum(1 for t in tasks if progress_lookup.get(t.id) and progress_lookup[t.id].status == "completed")
        st.markdown(
            f"## {mission.title}\n{mission.description}\n\nStage: {mission.stage or 'Any'} | Progress: {completed}/{len(tasks)} | Reward: {mission.total_xp_reward} XP"
        )
        for task in tasks:
            render_task_row(trainee, task, progress_lookup, storage)
        st.divider()


if __name__ == "__main__":
    main()
