from __future__ import annotations

from pathlib import Path

import streamlit as st

from config.settings import settings
from core.storage import get_storage


def load_styles() -> None:
    style_path = Path(__file__).parent / "assets" / "styles.css"
    if style_path.exists():
        st.markdown(f"<style>{style_path.read_text()}</style>", unsafe_allow_html=True)


def render_sidebar(storage) -> None:
    st.sidebar.image(settings.logo_path, caption="HB Portal", width=160)
    mode = st.sidebar.selectbox("Mode", ["Trainee", "Admin"], index=0)
    st.session_state["mode"] = mode

    if mode == "Trainee":
        trainees = storage.list_trainees()
        trainee_map = {t.name: t.id for t in trainees}
        selected_name = st.sidebar.selectbox("Select your name", list(trainee_map.keys())) if trainees else None
        if selected_name:
            st.session_state["trainee_id"] = trainee_map[selected_name]
            st.sidebar.success("Loaded trainee profile")
    else:
        password = st.sidebar.text_input("Admin password", type="password")
        if password:
            if password == settings.admin_password:
                st.session_state["is_admin"] = True
                st.sidebar.success("Admin mode enabled")
            else:
                st.session_state["is_admin"] = False
                st.sidebar.error("Incorrect password")


st.set_page_config(page_title="HB Portal", page_icon="🍜", layout="wide")
storage = get_storage()
load_styles()
render_sidebar(storage)

st.title("HB Portal")
st.caption("Journey tracker for Hawker Boys trainees")

mode = st.session_state.get("mode", "Trainee")
if mode == "Trainee":
    trainee_id = st.session_state.get("trainee_id")
    if trainee_id:
        trainee = storage.get_trainee(trainee_id)
        if trainee:
            st.success(f"Welcome back, {trainee.name}.")
        else:
            st.warning("Select a trainee profile from the sidebar.")
    else:
        st.info("Choose your trainee profile from the sidebar to view pages.")
else:
    if st.session_state.get("is_admin"):
        st.success("Admin mode active. Open the Admin page to manage data.")
    else:
        st.warning("Enter the admin password in the sidebar to unlock admin tools.")

st.write("Use the page selector on the left to explore missions, progress, and support.")
