"""
Admin endpoints for demo seeding and curation
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.database import get_db
from app.api.deps import get_current_admin_user, get_current_user
from app.models.users import User
from app.models.main_tables import Project, Task
from app.core.secrets import hash_password

router = APIRouter()


@router.post("/seed-demo")
def seed_demo(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Create demo users and curate 10 most-recently-updated projects with tasks."""
    # Bootstrap allowance: if no users exist, allow seeding without auth
    # Ensure users table exists (runtime bootstrap if migrations not applied)
    if db.bind is not None:
        inspector = inspect(db.bind)
        if not inspector.has_table('users'):
            User.__table__.create(bind=db.bind, checkfirst=True)

    user_count = db.query(User).count() if db.bind else 0
    if user_count > 0:
        if (current_user.get("role") or "").lower() != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    users = [
        ("owner.jaya@example.com", "Jaya Owner", "owner"),
        ("leader.karan@example.com", "Karan Leader", "portfolio"),
        ("admin.anu@example.com", "Anu Admin", "admin"),
    ]

    created_users = []
    for email, name, role in users:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            creds = hash_password("ChangeMe!123")
            u = User(
                email=email,
                name=name,
                role=role,
                password_hash=creds["hash"],
                password_salt=creds["salt"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(u)
            created_users.append(email)

    # curate projects
    demo_projects: List[Project] = db.query(Project).order_by(Project.updated_at.desc().nullslast()).limit(10).all()
    # Ensure each has at least a few tasks
    for p in demo_projects:
        existing = db.query(Task).filter(Task.project_id == p.id).count()
        to_create = max(0, 5 - existing)
        for i in range(to_create):
            t = Task(
                project_id=p.id,
                task_name=f"Demo Task {i+1}",
                description="Seeded demo task",
                start_date=p.start_date,
                due_date=p.due_date,
                percent_complete=0,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(t)

    db.commit()
    return {
        "created_users": created_users,
        "curated_project_count": len(demo_projects)
    }


