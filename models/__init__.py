from datetime import datetime, timezone

from ..extentions import db


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(120), nullable=False)
    experience_level = db.Column(db.String(40), nullable=False, default="mid-level")
    interview_type = db.Column(db.String(40), nullable=False, default="mixed")
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )
    questions = db.relationship(
        "InterviewQuestion",
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.position",
        lazy="selectin",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "experience_level": self.experience_level,
            "interview_type": self.interview_type,
            "status": self.status,
            "created_at": _isoformat(self.created_at),
            "updated_at": _isoformat(self.updated_at),
            "questions": [question.to_dict() for question in self.questions],
        }


class InterviewQuestion(db.Model):
    __tablename__ = "interview_questions"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(
        db.Integer, db.ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False
    )
    position = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    interview = db.relationship("Interview", back_populates="questions")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "position": self.position,
            "text": self.text,
            "answer": self.answer,
            "created_at": _isoformat(self.created_at),
        }


__all__ = ["Interview", "InterviewQuestion"]