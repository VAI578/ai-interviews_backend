from typing import TypeVar

from sqlalchemy import select

from ..extentions import db
from ..models import Interview, InterviewQuestion

Entity = TypeVar("Entity", Interview, InterviewQuestion)


def list_interviews(status: str | None = None) -> list[Interview]:
    statement = select(Interview).order_by(Interview.created_at.desc())
    if status is not None:
        statement = statement.where(Interview.status == status)
    return list(db.session.scalars(statement).all())


def get_interview(interview_id: int) -> Interview | None:
    return db.session.get(Interview, interview_id)


def get_question(question_id: int) -> InterviewQuestion | None:
    return db.session.get(InterviewQuestion, question_id)


def save(entity: Entity) -> Entity:
    db.session.add(entity)
    db.session.commit()
    return entity


def delete_interview(interview: Interview) -> None:
    db.session.delete(interview)
    db.session.commit()