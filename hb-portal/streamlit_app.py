from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import base64

import streamlit as st

from streamlit_data import DATA_FILE, load_data, new_id, reset_data, save_data

ASSETS_DIR = Path(__file__).parent / "Assets"
LOGO_PATH = ASSETS_DIR / "Logo_bgr.png"
ICON_BG_PATH = ASSETS_DIR / "icon_bgr.png"

st.set_page_config(page_title="Hawker Boys Portal", layout="wide", page_icon=str(LOGO_PATH if LOGO_PATH.exists() else "🔥"))


def load_logo_bytes() -> Optional[bytes]:
    for path in [LOGO_PATH, ASSETS_DIR / "Hawker_Boys_logo_new.png"]:
        if path.exists():
            return path.read_bytes()
    return None


def load_icon_data_uri() -> Optional[str]:
    path = ICON_BG_PATH
    if path.exists():
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    return None


# Global UI styling for the portal with optional watermark background.
background_image = load_icon_data_uri()
watermark_layer = (
    f"background-image: linear-gradient(rgba(247,243,236,0.92), rgba(247,243,236,0.92)), url('{background_image}');"
    "background-repeat: no-repeat;"
    "background-position: center 160px;"
    "background-size: 520px;"
    "background-attachment: fixed;"
    if background_image
    else "background: #F7F3EC;"
)

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&display=swap');
      .block-container {{ max-width: 1100px !important; padding-top: 1.5rem; padding-bottom: 2rem; }}
      html, body, .stApp {{
        font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
        color: #222222;
        background: #F7F3EC;
        {watermark_layer}
      }}
      .hb-section-title {{ font-family: 'Montserrat', 'Inter', sans-serif; font-size: 18px; font-weight: 700; margin: 18px 0 12px 0; padding-bottom: 6px; border-bottom: 2px solid #F26A21; color: #222222; }}
      .hb-section {{ font-family: 'Montserrat', 'Inter', sans-serif; font-size: 18px; font-weight: 700; margin: 18px 0 6px 0; color: #222222; }}
      .hb-card {{ background: #FFFFFF; border: 1px solid #E2E2E2; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
      .hb-ann-title {{ font-weight: 700; font-size: 16px; color: #222222; margin-bottom: 4px; }}
      .hb-ann-date {{ font-size: 12px; color: #6C6C6C; margin-bottom: 6px; }}
      .hb-progress-label {{ font-weight: 600; font-size: 14px; margin-top: 8px; margin-bottom: 4px; }}
      .hb-eyebrow {{ color: #F26A21; letter-spacing: 0.08em; font-size: 12px; text-transform: uppercase; margin-bottom: 4px; }}
      .hb-title {{ font-family: 'Montserrat', 'Inter', sans-serif; font-weight: 700; color: #1F1F1F; margin: 0 0 6px 0; font-size: 26px; line-height: 1.2; }}
      .hb-desc {{ color: #3A3A3A; }}
      .hb-link {{ color: #F26A21; text-decoration: none; font-weight: 600; }}
      img[alt="streamlitApp"] {{ display: none; }}
    </style>
    """,
    unsafe_allow_html=True,
)

UPLOAD_DIR = Path(__file__).parent / "streamlit_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Two-page navigation; simple labels to keep the UI focused.
NAV_ITEMS: List[Tuple[str, str]] = [
    ("Dashboard", "Dashboard"),
    ("Uploads", "Uploads"),
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
    st.markdown(f"<h3 class='hb-section'>{title}</h3>", unsafe_allow_html=True)
    if description:
        st.markdown(f"<p class='hb-desc'>{description}</p>", unsafe_allow_html=True)


def render_home(data: Dict[str, Any]) -> None:
    hero = st.container()
    with hero:
        cols = st.columns([1, 3])
        with cols[0]:
            logo_bytes = load_logo_bytes()
            if logo_bytes:
                st.image(logo_bytes, width=150)
        with cols[1]:
            st.markdown("<div class='hb-hero'>", unsafe_allow_html=True)
            st.markdown("<div class='hb-eyebrow'>Hawker Boys · From humble beginnings</div>", unsafe_allow_html=True)
            st.markdown("<div class='hb-title'>Hawker Boys Portal</div>", unsafe_allow_html=True)
            st.markdown("<div class='hb-desc'>Announcements first, then programme health at a glance. Admins sign in from the sidebar for extra controls.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Programme health metrics
    metrics_cols = st.columns(3)
    metrics_cols[0].metric("Active trainees", len(data["trainees"]))
    # WSQ completion reuses existing calculation.
    certs_total = len(data["trainee_certifications"])
    quests_total = len(data["quest_progress"]) or 1
    wsq_completion_rate = min(int((certs_total / quests_total) * 100), 100)
    metrics_cols[1].metric("WSQ completion rate", f"{wsq_completion_rate}%")
    placed = sum(1 for s in data["shifts"] if s.get("status") == "CONFIRMED")
    metrics_cols[2].metric("Placed in stalls", placed)

    st.markdown("<div class='hb-section-title'>Announcements & updates</div>", unsafe_allow_html=True)
    ann_col1, ann_col2 = st.columns([2, 1])
    with ann_col1:
        announcements = sorted(data["announcements"], key=lambda a: a["published_at"], reverse=True)[:4]
        for ann in announcements:
            st.markdown(
                f"""
                <div class="hb-card">
                  <div class="hb-ann-title">{ann['title']}</div>
                  <div class="hb-ann-date">{fmt_date(ann['published_at'])}</div>
                  <div>{ann['body']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with ann_col2:
        # Upcoming/this week summary (placeholder uses first shift/compliance if available).
        upcoming_shift = sorted(data["shifts"], key=lambda s: s["start"])[0] if data["shifts"] else None
        upcoming_compliance = sorted(data["compliance_events"], key=lambda e: e["start"])[0] if data["compliance_events"] else None
        summary_lines = []
        if upcoming_shift:
            summary_lines.append(f"Shift: {fmt_date(upcoming_shift['start'], True)} @ {upcoming_shift['location']}")
        if upcoming_compliance:
            summary_lines.append(f"Compliance: {upcoming_compliance['type']} on {fmt_date(upcoming_compliance['start'])}")
        if not summary_lines:
            summary_lines.append("No scheduled items this week. Add upcoming shifts to surface here.")
        st.markdown(
            f"""
            <div class="hb-card">
              <div class="hb-ann-title">This week</div>
              <div class="hb-ann-date">Snapshot of key events</div>
              <div>{"<br/>".join(summary_lines)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='hb-section-title'>Progress & achievements</div>", unsafe_allow_html=True)
    progress_cols = st.columns([3, 1])

    # Left: stacked KPIs
    with progress_cols[0]:
        trainee = data["trainees"][0] if data["trainees"] else None
        if trainee:
            trainee_id = trainee["id"]
            certs = [c for c in data["trainee_certifications"] if c["trainee_id"] == trainee_id]
            quests = [q for q in data["quest_progress"] if q["trainee_id"] == trainee_id]
            completion = int((len(certs) / max(1, len(quests) or 1)) * 100)
        else:
            completion = 0

        mentor_sessions = len(data["assessments"])
        mentor_goal = max(1, len(data["trainees"]) * 2)
        mentor_attendance = min(int((mentor_sessions / mentor_goal) * 100), 100)

        feedback_positive = sum(1 for f in data["customer_feedback"] if f.get("rating", 0) >= 4)
        feedback_total = max(1, len(data["customer_feedback"]))
        feedback_rate = min(int((feedback_positive / feedback_total) * 100), 100)

        st.markdown("<div class='hb-progress-label'>WSQ completion vs goal</div>", unsafe_allow_html=True)
        st.progress(completion)
        st.markdown("<div class='hb-progress-label'>Mentor session attendance</div>", unsafe_allow_html=True)
        st.progress(mentor_attendance)
        st.markdown("<div class='hb-progress-label'>Positive feedback rate</div>", unsafe_allow_html=True)
        st.progress(feedback_rate)

    # Right: quests & badges card
    with progress_cols[1]:
        st.markdown(
            """
            <div class="hb-card">
              <div class="hb-ann-title">Quests & badges</div>
              <div class="hb-ann-date">View trainee quests and earned badges.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Open quests view")

    page_title("Shifts, compliance, and support")
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

    page_title("Feedback pulse")
    feedback = sorted(data["customer_feedback"], key=lambda f: f["created_at"], reverse=True)[:5]
    for item in feedback:
        trainee_name = lookup_by_id(data["trainees"], item["trainee_id"]) or item["trainee_id"]
        st.write(f"- {trainee_name}: {item['rating']}/5 — {item['comment']}")

    # Admin extras
    if st.session_state.get("hb_user", {}).get("role") == "ADMIN":
        page_title("Admin controls")
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

    nav_labels = [label for label, _ in NAV_ITEMS]
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
