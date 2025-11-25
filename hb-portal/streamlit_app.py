from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from streamlit_data import DATA_FILE, load_data, new_id, reset_data, save_data

st.set_page_config(page_title="Hawker Boys Portal (Streamlit)", layout="wide", page_icon="🔥")

UPLOAD_DIR = Path(__file__).parent / "streamlit_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Two-page navigation with icon labels.
NAV_ITEMS: List[Tuple[str, str]] = [
    ("Dashboard", "🏠"),
    ("Uploads", "📁"),
]


def get_data() -> Dict[str, Any]:
    if "hb_data" not in st.session_state:
        st.session_state["hb_data"] = load_data()
    return st.session_state["hb_data"]


def persist_data() -> None:
    save_data(st.session_state["hb_data"])


def fmt_date(value: str, with_time: bool = False) -> str:
    dt = datetime.fromisoformat(value)
    return dt.strftime("%d %b %Y %H:%M") if with_time else dt.strftime("%d %b %Y")


def lookup_by_id(items: List[Dict[str, Any]], item_id: str, label: str = "name") -> Optional[str]:
    for item in items:
        if item["id"] == item_id:
            return item.get(label)
    return None


def page_title(title: str, description: str | None = None) -> None:
    st.markdown("<div class='hb-eyebrow'>Hawker Boys · From humble beginnings</div>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='hb-title'>{title}</h2>", unsafe_allow_html=True)
    if description:
        st.markdown(f"<p class='hb-desc'>{description}</p>", unsafe_allow_html=True)


def inject_brand_css() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&display=swap');
          html, body, [class^="st"] {
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
            color: #F5F5F5;
            background: #0D0D0D;
          }
          .hb-title { font-family: 'Montserrat', 'Inter', sans-serif; font-weight: 700; color: #F5F5F5; margin: 0 0 6px 0; }
          .hb-eyebrow { color: #FF6B00; letter-spacing: 0.08em; font-size: 12px; text-transform: uppercase; margin-bottom: 4px; }
          .hb-desc { color: #B8B8B8; }
          .stProgress > div > div { background: linear-gradient(90deg, #FF6B00, #C44A00); }
          .hb-card { background: #2A2A2A; border: 1px solid #6C6C6C; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
          .hb-chip { display: inline-block; background: rgba(255,107,0,0.12); color: #FF6B00; padding: 4px 10px; border-radius: 999px; font-size: 12px; }
          .stDownloadButton button, .stButton button { background: #FF6B00; color: #0D0D0D; border: none; }
          .stDownloadButton button:hover, .stButton button:hover { background: #C44A00; color: #0D0D0D; }
          .stTextInput > div > input, textarea, select { background: #1A1A1A !important; color: #F5F5F5 !important; border-radius: 8px; border: 1px solid #6C6C6C; }
          .stSlider > div[data-baseweb="slider"] > div { background: #FF6B00 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home(data: Dict[str, Any]) -> None:
    page_title("One-page portal", "Announcements up front, with program snapshots below. Admin controls unlock after admin sign-in.")

    hero_cols = st.columns([3, 2])
    with hero_cols[0]:
        st.markdown(
            """
            <div class="hb-card">
              <div class="hb-chip">Latest</div>
              <h3 style="margin:6px 0 4px 0;">Announcements</h3>
            """,
            unsafe_allow_html=True,
        )
        announcements = sorted(data["announcements"], key=lambda a: a["published_at"], reverse=True)[:3]
        for ann in announcements:
            st.markdown(f"- **{ann['title']}** — {ann['body']}  \n<span style='color:#B8B8B8;'>{fmt_date(ann['published_at'])}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with hero_cols[1]:
        st.markdown(
            """
            <div class="hb-card">
              <div class="hb-chip">Pulse</div>
              <h3 style="margin:6px 0 4px 0;">Programme snapshot</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns(3)
        cols[0].metric("Trainees", len(data["trainees"]))
        cols[1].metric("Mentors", len(data["mentors"]))
        cols[2].metric("Employers", len(data["employers"]))

    # Progress & quests
    st.markdown("### Progress & Achievements")
    progress_cols = st.columns(2)
    trainee = data["trainees"][0] if data["trainees"] else None
    if trainee:
        trainee_id = trainee["id"]
        certs = [c for c in data["trainee_certifications"] if c["trainee_id"] == trainee_id]
        quests = [q for q in data["quest_progress"] if q["trainee_id"] == trainee_id]
        completion = int((len(certs) / max(1, len(quests) or 1)) * 100)
        completion_display = min(completion, 100)
        progress_cols[0].progress(completion_display, text=f"{completion_display}% WSQ completion vs quests")
        progress_cols[0].markdown("**Certifications**")
        for cert in certs:
            cert_meta = lookup_by_id(data["certifications"], cert["certification_id"], "name")
            progress_cols[0].write(f"- {cert_meta or 'Certification'} ({fmt_date(cert['issued_at'])})")
        progress_cols[1].markdown("**Quests & Badges**")
        for row in quests:
            quest = next((q for q in data["quests"] if q["id"] == row["quest_id"]), None)
            if quest:
                progress_cols[1].write(f"- {quest['title']} · {row['status']} · {quest['points']} pts")
        earned_ids = {b["badge_id"] for b in data["trainee_badges"] if b["trainee_id"] == trainee_id}
        for badge in data["badges"]:
            if badge["id"] in earned_ids:
                progress_cols[1].write(f"🏅 {badge['title']} — {badge['description']}")

    st.markdown("### Shifts, Compliance, and Support")
    ops_cols = st.columns(3)
    shifts = sorted(data["shifts"], key=lambda s: s["start"])
    with ops_cols[0]:
        st.markdown("**Upcoming shifts**")
        for shift in shifts[:4]:
            st.write(f"- {fmt_date(shift['start'], True)} · {shift['location']} · {shift['status']}")
    with ops_cols[1]:
        st.markdown("**Compliance**")
        for event in sorted(data["compliance_events"], key=lambda e: e["start"])[:4]:
            st.write(f"- {event['type']} · {fmt_date(event['start'])}")
    with ops_cols[2]:
        st.markdown("**Support tickets**")
        tickets = sorted(data["support_tickets"], key=lambda t: t["created_at"], reverse=True)[:4]
        if tickets:
            for ticket in tickets:
                st.write(f"- {ticket['category']} · {ticket['message']} ({ticket['status']})")
        else:
            st.write("All clear.")

    st.markdown("### Feedback pulse")
    feedback = sorted(data["customer_feedback"], key=lambda f: f["created_at"], reverse=True)[:5]
    for item in feedback:
        trainee_name = lookup_by_id(data["trainees"], item["trainee_id"]) or item["trainee_id"]
        st.write(f"- {trainee_name}: {item['rating']}/5 — {item['comment']}")

    # Admin extras
    if st.session_state.get("hb_user", {}).get("role") == "ADMIN":
        st.markdown("### Admin controls")
        role_counts = Counter(user["role"] for user in data["users"])
        cols = st.columns(4)
        for idx, role in enumerate(["TRAINEE", "MENTOR", "EMPLOYER", "ADMIN"]):
            cols[idx].metric(role.title(), role_counts.get(role, 0))
        csv_content = feedback_csv(data)
        st.download_button("Download customer feedback CSV", data=csv_content, file_name="customer-feedback.csv", mime="text/csv")
        st.caption(f"Data stored locally at {DATA_FILE}")


def render_uploads(data: Dict[str, Any]) -> None:
    page_title("Secure uploads", "Medical leave, bank, and official correspondence.")
    for doc in sorted(data["secure_documents"], key=lambda d: d["created_at"], reverse=True):
        owner = doc["owner_type"]
        name = lookup_by_id(data["trainees"], doc["trainee_id"]) or lookup_by_id(data["employers"], doc["employer_id"], "company_name") or "Unknown"
        st.write(f"- {doc['category']} · {doc['filename']} ({owner}: {name})")

    st.subheader("Upload new document")
    with st.form("upload-form"):
        owner_type = st.selectbox("Owner type", ["TRAINEE", "EMPLOYER"])
        trainee_id = None
        employer_id = None
        if owner_type == "TRAINEE":
            trainee = st.selectbox("Trainee", data["trainees"], format_func=lambda t: t["name"])
            trainee_id = trainee["id"]
        else:
            employer = st.selectbox("Employer", data["employers"], format_func=lambda e: e["company_name"])
            employer_id = employer["id"]
        category = st.selectbox("Category", ["MC", "BANK", "OFFICIAL", "OTHER"])
        file = st.file_uploader("Choose file")
        submitted = st.form_submit_button("Upload")
        if submitted and file:
            storage_key = f"{new_id('upload')}-{file.name}"
            path = UPLOAD_DIR / storage_key
            path.write_bytes(file.getbuffer())
            data["secure_documents"].insert(
                0,
                {
                    "id": new_id("doc"),
                    "owner_type": owner_type,
                    "trainee_id": trainee_id,
                    "employer_id": employer_id,
                    "category": category,
                    "filename": file.name,
                    "mime": file.type,
                    "size": file.size,
                    "storage_key": storage_key,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )
            persist_data()
            st.success(f"Uploaded {file.name}")


def feedback_csv(data: Dict[str, Any]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["traineeName", "rating", "comment", "receiptCode", "createdAt"])
    for row in data["customer_feedback"]:
        trainee_name = lookup_by_id(data["trainees"], row["trainee_id"]) or row["trainee_id"]
        writer.writerow([trainee_name, row["rating"], row["comment"], row.get("receipt_code", ""), row["created_at"]])
    return buffer.getvalue()


def render_public_feedback(data: Dict[str, Any]) -> None:
    trainees = data["trainees"]
    with st.form("feedback-form", clear_on_submit=True):
        trainee = st.selectbox("Trainee", trainees, format_func=lambda t: t["name"])
        rating = st.slider("Rating", min_value=1, max_value=5, value=5)
        comment = st.text_area("Comment", height=120)
        receipt_code = st.text_input("Optional receipt code")
        submitted = st.form_submit_button("Share feedback")
        if submitted and comment:
            data["customer_feedback"].insert(
                0,
                {
                    "id": new_id("fb"),
                    "trainee_id": trainee["id"],
                    "rating": int(rating),
                    "comment": comment,
                    "receipt_code": receipt_code,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )
            persist_data()
            st.success("Thank you for championing our trainees!")

    st.subheader("Recent feedback")
    for row in sorted(data["customer_feedback"], key=lambda f: f["created_at"], reverse=True)[:10]:
        trainee_name = lookup_by_id(trainees, row["trainee_id"]) or row["trainee_id"]
        st.write(f"- {trainee_name}: {row['rating']}/5 — {row['comment']} ({fmt_date(row['created_at'])})")


def sidebar_nav() -> str:
    st.sidebar.markdown("### 🔥 Hawker Boys")
    st.sidebar.caption("From humble beginnings · Light emerging from darkness")

    # Lightweight login gate: defaults to regular user; admin unlocks extras.
    if "hb_user" not in st.session_state:
        st.session_state["hb_user"] = {"email": "trainee@hawkerboys.com", "role": "USER"}

    with st.sidebar.form("login-form"):
        email = st.text_input("Email", value=st.session_state["hb_user"]["email"])
        role = st.selectbox("Role", ["USER", "ADMIN"], index=0)
        submitted = st.form_submit_button("Sign in")
        if submitted:
            st.session_state["hb_user"] = {"email": email, "role": role}
            st.success(f"Signed in as {role}")

    nav_labels = [f"{icon} {label}" for label, icon in NAV_ITEMS]
    nav_choice = st.sidebar.radio("Navigation", nav_labels)
    nav = NAV_ITEMS[nav_labels.index(nav_choice)][0]

    st.sidebar.markdown("**Demo accounts**")
    st.sidebar.caption("Regular: trainee@hawkerboys.com  \nAdmin: admin@hawkerboys.com")

    if st.sidebar.button("Reset sample data"):
        st.session_state["hb_data"] = reset_data()
        st.sidebar.success("Seed data restored.")
        st.rerun()

    st.sidebar.caption("Uploads live on their own page; everything else is on the dashboard.")
    return nav


def main() -> None:
    inject_brand_css()
    data = get_data()
    nav = sidebar_nav()

    if nav == "Dashboard":
        render_home(data)
    elif nav == "Uploads":
        render_uploads(data)
    else:
        render_home(data)


if __name__ == "__main__":
    main()
