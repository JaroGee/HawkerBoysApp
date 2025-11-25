from __future__ import annotations

from datetime import datetime

import streamlit as st

from core.models import SupportRequest
from core.storage import get_storage


CONTACTS = {
    "Training support": "training@hawkerboys.sg",
    "Life and family support": "care@hawkerboys.sg",
}


def main() -> None:
    st.title("Support")
    storage = get_storage()
    trainee_id = st.session_state.get("trainee_id")
    if not trainee_id:
        st.info("Select your trainee profile from the sidebar to request support.")
        return

    st.subheader("Contacts")
    for label, email in CONTACTS.items():
        st.markdown(f"- **{label}:** {email}")

    st.divider()
    st.subheader("Request help")
    category = st.selectbox("Category", ["Training", "Placement", "Personal Support", "Other"])
    message = st.text_area("Share how we can help")
    if st.button("Submit request"):
        if not message.strip():
            st.error("Please enter a message before submitting.")
        else:
            request = SupportRequest(
                id=f"support-{datetime.utcnow().timestamp()}",
                trainee_id=trainee_id,
                message=message,
                category=category,
                status="new",
            )
            storage.save_support_request(request)
            st.success("Request received. A team member will contact you soon.")


if __name__ == "__main__":
    main()
