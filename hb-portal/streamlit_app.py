from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from streamlit_data import DATA_FILE, load_data, new_id, reset_data, save_data

st.set_page_config(page_title="Hawker Boys Portal (Streamlit)", layout="wide", page_icon="🍜")

UPLOAD_DIR = Path(__file__).parent / "streamlit_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

NAV_ITEMS = [
    "Home",
    "Trainee dashboard",
    "Mentor dashboard",
    "Employer dashboard",
    "Admin dashboard",
    "Announcements",
    "Progress",
    "Quests",
    "Badges",
    "Schedule & compliance",
    "Messages",
    "Uploads",
    "Help",
    "Public feedback",
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
    st.markdown("### 🍜 Hawker Boys Portal")
    st.markdown(f"## {title}")
    if description:
        st.caption(description)


def render_home(data: Dict[str, Any]) -> None:
    page_title("Streamlit experience", "Role-aware PDPA-friendly portal translated from the Next.js app.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Trainees", len(data["trainees"]))
    col2.metric("Mentors", len(data["mentors"]))
    col3.metric("Employers", len(data["employers"]))

    st.markdown(
        """
        **Unified training journeys** — Track WSQ certifications, quests, compliance, and shifts in one workspace.  
        **Mentor intelligence** — Assessment templates, aftercare, and live check-ins stay in one place.  
        **Employer-ready** — Shift planning, attendance, and customer feedback loops give instant context.
        """
    )
    st.info("Use the sidebar to move between dashboards, announcements, quests, uploads, and the public feedback form.")


def render_trainee_dashboard(data: Dict[str, Any]) -> None:
    page_title("Trainee dashboard", "Progress, shifts, and announcements for a selected trainee.")
    trainee = st.selectbox("Choose trainee", data["trainees"], format_func=lambda t: t["name"])
    trainee_id = trainee["id"]

    certs = [c for c in data["trainee_certifications"] if c["trainee_id"] == trainee_id]
    quests = [q for q in data["quest_progress"] if q["trainee_id"] == trainee_id]
    completion = int((len(certs) / max(1, len(quests) or 1)) * 100)
    completion_display = min(completion, 100)

    st.progress(completion_display, text=f"{completion_display}% completion based on certifications vs quests")

    col1, col2 = st.columns(2)
    col1.subheader("WSQ achievements")
    if certs:
        for cert in certs:
            cert_meta = lookup_by_id(data["certifications"], cert["certification_id"], "name")
            col1.write(f"- {cert_meta or 'Certification'} · issued {fmt_date(cert['issued_at'])}")
    else:
        col1.write("No certifications yet.")

    col2.subheader("Quests")
    for quest_row in quests[:5]:
        quest = next((q for q in data["quests"] if q["id"] == quest_row["quest_id"]), None)
        if quest:
            col2.write(f"- {quest['title']} · {quest_row['status']} ({quest['points']} pts)")

    st.divider()

    st.subheader("Upcoming shifts")
    upcoming_shifts = sorted(
        [s for s in data["shifts"] if s["trainee_id"] == trainee_id],
        key=lambda s: s["start"],
    )
    for shift in upcoming_shifts:
        st.write(f"**{shift['location']}** · {fmt_date(shift['start'], True)} · {shift['status']}")

    st.subheader("Announcements")
    targeted = [a for a in data["announcements"] if a["audience"] in ("ALL", "TRAINEES")]
    for ann in sorted(targeted, key=lambda a: a["published_at"], reverse=True):
        st.write(f"**{ann['title']}** — {ann['body']} ({ann['audience']})")


def render_mentor_dashboard(data: Dict[str, Any]) -> None:
    page_title("Mentor ops", "Recent assessments and open aftercare tickets.")
    assessments = sorted(data["assessments"], key=lambda a: a["created_at"], reverse=True)
    tickets = [t for t in data["support_tickets"] if t.get("status") != "CLOSED"]

    st.subheader("Recent assessments")
    rows = []
    for row in assessments:
        trainee_name = lookup_by_id(data["trainees"], row["trainee_id"]) or row["trainee_id"]
        template = lookup_by_id(data["assessment_templates"], row["template_id"], "name") or "Template"
        score_text = ", ".join(f"{s['key']}: {s['value']}" for s in row.get("scores", []))
        rows.append(
            {
                "Trainee": trainee_name,
                "Template": template,
                "Scores": score_text,
                "Created": fmt_date(row["created_at"]),
                "Notes": row.get("notes", ""),
            }
        )
    st.dataframe(rows, use_container_width=True)

    st.subheader("Support tickets")
    if tickets:
        for ticket in tickets:
            name = lookup_by_id(data["trainees"], ticket["trainee_id"]) or ticket["trainee_id"]
            st.write(f"- **{name}** · {ticket['category']} · {ticket['message']} ({ticket['status']})")
    else:
        st.write("No open tickets.")


def render_employer_dashboard(data: Dict[str, Any]) -> None:
    page_title("Employer hub", "Plan shifts and review customer sentiment.")
    shifts = sorted(data["shifts"], key=lambda s: s["start"])
    feedback = sorted(data["customer_feedback"], key=lambda f: f["created_at"], reverse=True)

    st.subheader("Shift planner")
    for shift in shifts:
        trainee_name = lookup_by_id(data["trainees"], shift["trainee_id"]) or shift["trainee_id"]
        employer_name = lookup_by_id(data["employers"], shift["employer_id"], "company_name") or shift["employer_id"]
        st.write(f"- {fmt_date(shift['start'], True)} · {shift['location']} · {trainee_name} ({employer_name}) — {shift['status']}")

    st.subheader("Customer feedback pulse")
    for item in feedback:
        trainee_name = lookup_by_id(data["trainees"], item["trainee_id"]) or item["trainee_id"]
        st.write(f"- {trainee_name}: {item['rating']}/5 — {item['comment']}")


def feedback_csv(data: Dict[str, Any]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["traineeName", "rating", "comment", "receiptCode", "createdAt"])
    for row in data["customer_feedback"]:
        trainee_name = lookup_by_id(data["trainees"], row["trainee_id"]) or row["trainee_id"]
        writer.writerow([trainee_name, row["rating"], row["comment"], row.get("receipt_code", ""), row["created_at"]])
    return buffer.getvalue()


def render_admin_dashboard(data: Dict[str, Any]) -> None:
    page_title("Admin control center", "Counts, announcements, audit log, and exports.")
    role_counts = Counter(user["role"] for user in data["users"])
    cols = st.columns(4)
    for idx, role in enumerate(["TRAINEE", "MENTOR", "EMPLOYER", "ADMIN"]):
        cols[idx].metric(role.title(), role_counts.get(role, 0))

    st.subheader("Announcements")
    for ann in sorted(data["announcements"], key=lambda a: a["published_at"], reverse=True)[:5]:
        st.write(f"- **{ann['title']}** · {ann['audience']} · {fmt_date(ann['published_at'])}")

    st.subheader("Audit log")
    for event in sorted(data["audit_events"], key=lambda a: a["at"], reverse=True):
        st.write(f"- {event['actor_role']} {event['action']} {event['entity']} @ {fmt_date(event['at'], True)}")

    csv_content = feedback_csv(data)
    st.download_button("Download customer feedback CSV", data=csv_content, file_name="customer-feedback.csv", mime="text/csv")
    st.caption(f"Data stored locally at {DATA_FILE}")


def render_announcements(data: Dict[str, Any]) -> None:
    page_title("Announcements", "Create and browse platform updates.")
    with st.form("announcement-form", clear_on_submit=True):
        title = st.text_input("Title")
        body = st.text_area("Body", height=120)
        audience = st.selectbox("Audience", ["ALL", "TRAINEES", "MENTORS", "EMPLOYERS"])
        submitted = st.form_submit_button("Publish announcement")
        if submitted and title and body:
            data["announcements"].insert(
                0,
                {"id": new_id("ann"), "title": title, "body": body, "audience": audience, "published_at": datetime.utcnow().isoformat()},
            )
            persist_data()
            st.success("Announcement published.")

    st.divider()
    for ann in sorted(data["announcements"], key=lambda a: a["published_at"], reverse=True):
        st.write(f"**{ann['title']}** · {ann['audience']} · {fmt_date(ann['published_at'])}")
        st.caption(ann["body"])


def render_progress(data: Dict[str, Any]) -> None:
    page_title("Progress & achievements", "WSQ milestones, quests, and badges.")
    trainee = st.selectbox("Choose trainee", data["trainees"], format_func=lambda t: t["name"], key="progress-trainee")
    trainee_id = trainee["id"]

    certs = [c for c in data["trainee_certifications"] if c["trainee_id"] == trainee_id]
    quests = [q for q in data["quest_progress"] if q["trainee_id"] == trainee_id]
    completion = int((len(certs) / max(1, len(quests) or 1)) * 100)
    completion_display = min(completion, 100)
    st.progress(completion_display, text=f"{completion_display}% WSQ completion vs quests")

    st.subheader("Certifications")
    for cert in certs:
        meta = lookup_by_id(data["certifications"], cert["certification_id"], "name") or "Certification"
        st.write(f"- {meta} ({fmt_date(cert['issued_at'])})")

    st.subheader("Quest progress")
    for row in quests:
        quest = next((q for q in data["quests"] if q["id"] == row["quest_id"]), None)
        if quest:
            st.write(f"- {quest['title']} · {row['status']} · {quest['points']} pts")


def render_quests(data: Dict[str, Any]) -> None:
    page_title("Quests", "Active and upcoming quests for trainees.")
    trainee = st.selectbox("Choose trainee", data["trainees"], format_func=lambda t: t["name"], key="quests-trainee")
    trainee_id = trainee["id"]

    statuses = {row["quest_id"]: row["status"] for row in data["quest_progress"] if row["trainee_id"] == trainee_id}
    for quest in sorted(data["quests"], key=lambda q: q["start_at"] or ""):
        status = statuses.get(quest["id"], "LOCKED")
        window = f"{fmt_date(quest['start_at'])} — {fmt_date(quest['end_at'])}" if quest.get("end_at") else "Open"
        st.write(f"**{quest['title']}** · {quest['description']} · {quest['points']} pts · {status} · {window}")


def render_badges(data: Dict[str, Any]) -> None:
    page_title("Badges & ranks", "Available badges and earned highlights.")
    trainee = st.selectbox("Choose trainee", data["trainees"], format_func=lambda t: t["name"], key="badges-trainee")
    trainee_id = trainee["id"]
    earned_ids = {b["badge_id"] for b in data["trainee_badges"] if b["trainee_id"] == trainee_id}

    for badge in data["badges"]:
        earned = " (earned)" if badge["id"] in earned_ids else ""
        st.write(f"- {badge.get('icon', '')} {badge['title']} — {badge['description']}{earned}")


def render_schedule(data: Dict[str, Any]) -> None:
    page_title("Schedule & compliance", "Employer shifts and compliance events.")
    shifts = sorted(data["shifts"], key=lambda s: s["start"])
    st.subheader("Shifts")
    for shift in shifts:
        trainee_name = lookup_by_id(data["trainees"], shift["trainee_id"]) or shift["trainee_id"]
        st.write(f"- {fmt_date(shift['start'], True)} · {shift['location']} · {trainee_name} ({shift['status']})")

    st.subheader("Compliance")
    for event in sorted(data["compliance_events"], key=lambda e: e["start"]):
        st.write(f"- {event['type']} · {fmt_date(event['start'])} · {event.get('notes') or ''}")


def render_messages(data: Dict[str, Any]) -> None:
    page_title("Messages & aftercare", "Secure help desk threads and submissions.")
    tickets = sorted(data["support_tickets"], key=lambda t: t["created_at"], reverse=True)
    for ticket in tickets:
        trainee_name = lookup_by_id(data["trainees"], ticket["trainee_id"]) or ticket["trainee_id"]
        st.write(f"- {trainee_name} · {ticket['category']} · {ticket['message']} ({ticket['status']})")

    st.subheader("New support note")
    with st.form("support-form", clear_on_submit=True):
        trainee_choice = st.selectbox("Trainee (optional)", [""] + [t["name"] for t in data["trainees"]])
        category = st.selectbox("Category", ["AFTERCARE", "LOGIN", "GENERAL"])
        message = st.text_area("Message", height=120)
        submitted = st.form_submit_button("Send to ops")
        if submitted and message:
            trainee_id = next((t["id"] for t in data["trainees"] if t["name"] == trainee_choice), None) if trainee_choice else None
            data["support_tickets"].insert(
                0,
                {
                    "id": new_id("ticket"),
                    "trainee_id": trainee_id,
                    "category": category,
                    "message": message,
                    "status": "OPEN",
                    "created_at": datetime.utcnow().isoformat(),
                },
            )
            persist_data()
            st.success("Support note captured.")


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


def render_help(data: Dict[str, Any]) -> None:
    page_title("Help & aftercare", "Helplines and secure messaging.")
    st.subheader("Helplines")
    st.write("- Ops hotline: +65 6000 1234 (24/7 urgent matters)")
    st.write("- Aftercare WhatsApp: +65 8111 9999 (9am-9pm daily)")

    st.subheader("Secure message")
    note = st.text_area("How can we help?")
    if st.button("Send message", disabled=not note):
        data["support_tickets"].insert(
            0,
            {
                "id": new_id("ticket"),
                "trainee_id": None,
                "category": "HELP",
                "message": note,
                "status": "OPEN",
                "created_at": datetime.utcnow().isoformat(),
            },
        )
        persist_data()
        st.success("Message received by the ops team.")


def render_public_feedback(data: Dict[str, Any]) -> None:
    page_title("Public praise & feedback", "Quick form that mirrors the Turnstile-protected Next.js flow.")
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
    st.sidebar.markdown("### 🍜 Hawker Boys")
    nav = st.sidebar.radio("Navigation", NAV_ITEMS)
    if st.sidebar.button("Reset sample data"):
        st.session_state["hb_data"] = reset_data()
        st.sidebar.success("Seed data restored.")
        st.rerun()
    st.sidebar.caption("Streamlit app lives alongside the original Next.js codebase.")
    return nav


def main() -> None:
    data = get_data()
    nav = sidebar_nav()

    if nav == "Home":
        render_home(data)
    elif nav == "Trainee dashboard":
        render_trainee_dashboard(data)
    elif nav == "Mentor dashboard":
        render_mentor_dashboard(data)
    elif nav == "Employer dashboard":
        render_employer_dashboard(data)
    elif nav == "Admin dashboard":
        render_admin_dashboard(data)
    elif nav == "Announcements":
        render_announcements(data)
    elif nav == "Progress":
        render_progress(data)
    elif nav == "Quests":
        render_quests(data)
    elif nav == "Badges":
        render_badges(data)
    elif nav == "Schedule & compliance":
        render_schedule(data)
    elif nav == "Messages":
        render_messages(data)
    elif nav == "Uploads":
        render_uploads(data)
    elif nav == "Help":
        render_help(data)
    elif nav == "Public feedback":
        render_public_feedback(data)
    else:
        render_home(data)


if __name__ == "__main__":
    main()
