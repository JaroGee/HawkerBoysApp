from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "streamlit_data.json"


def _ts(hours_from_now: float = 0) -> str:
    """
    Return an ISO timestamp offset from now.
    """
    return (datetime.utcnow() + timedelta(hours=hours_from_now)).isoformat()


def default_data() -> Dict[str, Any]:
    now = datetime.utcnow()
    return {
        "users": [
            {"id": "user-admin", "email": "admin@hawkerboys.com", "role": "ADMIN"},
            {"id": "user-trainee", "email": "trainee@hawkerboys.com", "role": "TRAINEE"},
            {"id": "user-mentor", "email": "mentor@hawkerboys.com", "role": "MENTOR"},
            {"id": "user-employer", "email": "employer@hawkerboys.com", "role": "EMPLOYER"},
        ],
        "trainees": [
            {"id": "trainee-kai", "name": "Kai", "cohort": "2024A", "email": "trainee@hawkerboys.com"},
        ],
        "mentors": [
            {"id": "mentor-lee", "name": "Coach Lee", "email": "mentor@hawkerboys.com", "bio": "Former hawker hero"},
        ],
        "employers": [
            {"id": "employer-heritage", "company_name": "Heritage Bites", "email": "employer@hawkerboys.com"},
        ],
        "announcements": [
            {
                "id": "ann-1",
                "title": "New module launch",
                "body": "WSQ Food Safety 2 is open.",
                "audience": "TRAINEES",
                "published_at": now.isoformat(),
            },
            {
                "id": "ann-2",
                "title": "Mentor sync",
                "body": "Mentor standup on Friday.",
                "audience": "MENTORS",
                "published_at": now.isoformat(),
            },
            {
                "id": "ann-3",
                "title": "Public feedback",
                "body": "Share praise or concerns directly with the ops team.",
                "audience": "ALL",
                "published_at": now.isoformat(),
            },
        ],
        "certifications": [
            {"id": "cert-fs1", "code": "WSQ-FS1", "name": "WSQ Food Safety Level 1", "level": 1},
            {"id": "cert-fs2", "code": "WSQ-FS2", "name": "WSQ Food Safety Level 2", "level": 2},
            {"id": "cert-fs3", "code": "WSQ-FS3", "name": "WSQ Food Safety Level 3", "level": 3},
        ],
        "trainee_certifications": [
            {"id": "tc-1", "trainee_id": "trainee-kai", "certification_id": "cert-fs1", "issued_at": now.isoformat()},
        ],
        "quests": [
            {
                "id": "quest-1",
                "title": "Master mise en place",
                "description": "Prep station in under 10 minutes.",
                "points": 50,
                "start_at": now.isoformat(),
                "end_at": None,
            },
            {
                "id": "quest-2",
                "title": "Customer delight",
                "description": "Collect three 5-star ratings in a week.",
                "points": 80,
                "start_at": now.isoformat(),
                "end_at": _ts(24 * 7),
            },
        ],
        "quest_progress": [
            {"id": "qp-1", "quest_id": "quest-1", "trainee_id": "trainee-kai", "status": "ACTIVE", "updated_at": now.isoformat()},
            {"id": "qp-2", "quest_id": "quest-2", "trainee_id": "trainee-kai", "status": "LOCKED", "updated_at": now.isoformat()},
        ],
        "badges": [
            {"id": "badge-team", "code": "TEAM", "title": "Team Player", "description": "Praised by mentors", "icon": "🤝"},
            {"id": "badge-speed", "code": "SPEED", "title": "Speedster", "description": "Fastest prep of the cohort", "icon": "⚡"},
        ],
        "trainee_badges": [
            {"id": "tb-1", "trainee_id": "trainee-kai", "badge_id": "badge-team", "awarded_at": now.isoformat()},
        ],
        "customer_feedback": [
            {"id": "fb-1", "trainee_id": "trainee-kai", "rating": 5, "comment": "Friendly and fast!", "receipt_code": "ABC123", "created_at": now.isoformat()},
        ],
        "secure_documents": [
            {
                "id": "doc-1",
                "owner_type": "TRAINEE",
                "trainee_id": "trainee-kai",
                "employer_id": None,
                "category": "MC",
                "filename": "mc.pdf",
                "mime": "application/pdf",
                "size": 12000,
                "storage_key": "mc.pdf",
                "created_at": now.isoformat(),
            },
        ],
        "shifts": [
            {
                "id": "shift-1",
                "trainee_id": "trainee-kai",
                "employer_id": "employer-heritage",
                "start": (now + timedelta(days=1)).isoformat(),
                "end": (now + timedelta(days=1, hours=1)).isoformat(),
                "location": "Maxwell Food Centre",
                "status": "CONFIRMED",
            },
            {
                "id": "shift-2",
                "trainee_id": "trainee-kai",
                "employer_id": "employer-heritage",
                "start": (now + timedelta(days=3)).isoformat(),
                "end": (now + timedelta(days=3, hours=1)).isoformat(),
                "location": "Chinatown Complex",
                "status": "PLANNED",
            },
        ],
        "compliance_events": [
            {"id": "comp-1", "trainee_id": "trainee-kai", "type": "URINE_TEST", "start": (now + timedelta(days=2)).isoformat(), "notes": None},
            {"id": "comp-2", "trainee_id": "trainee-kai", "type": "APPOINTMENT", "start": (now + timedelta(days=5)).isoformat(), "notes": "Return to work check-in"},
        ],
        "support_tickets": [
            {"id": "ticket-1", "trainee_id": "trainee-kai", "category": "AFTERCARE", "message": "Need meal subsidy", "status": "OPEN", "created_at": now.isoformat()},
        ],
        "assessments": [
            {
                "id": "assess-1",
                "trainee_id": "trainee-kai",
                "mentor_id": "mentor-lee",
                "template_id": "template-1",
                "scores": [{"key": "speed", "value": 4}],
                "notes": "Great hustle",
                "created_at": now.isoformat(),
            },
        ],
        "assessment_templates": [
            {
                "id": "template-1",
                "name": "Stall readiness",
                "criteria": [{"key": "speed", "label": "Speed", "min": 1, "max": 5}],
            },
        ],
        "audit_events": [
            {"id": "audit-1", "actor_role": "ADMIN", "action": "seeded", "entity": "system", "at": now.isoformat()},
        ],
        "emergency_contacts": [
            {"id": "contact-1", "trainee_id": "trainee-kai", "name": "Mum", "relationship": "Mother", "phone": "+65 8888 2222", "email": None, "preferred": True},
        ],
    }


def load_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    data = default_data()
    save_data(data)
    return data


def save_data(data: Dict[str, Any]) -> Dict[str, Any]:
    DATA_FILE.write_text(json.dumps(data, indent=2))
    return data


def reset_data() -> Dict[str, Any]:
    data = default_data()
    save_data(data)
    return data


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"
