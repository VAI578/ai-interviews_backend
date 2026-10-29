from typing import Any

from ..extentions import db
from ..models import Interview, InterviewQuestion
from ..respositories import (
    delete_interview,
    get_interview,
    get_question,
    list_interviews,
    save,
)

ALLOWED_STATUSES = {"in_progress", "completed", "abandoned"}
MAX_QUESTIONS = 30


class ServiceError(ValueError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _required_text(
    payload: dict[str, Any], field: str, *, maximum_length: int
) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"'{field}' must be a non-empty string.")
    value = value.strip()
    if len(value) > maximum_length:
        raise ServiceError(f"'{field}' must be at most {maximum_length} characters.")
    return value


def _find_interview(interview_id: int) -> Interview:
    interview = get_interview(interview_id)
    if interview is None:
        raise ServiceError("Interview not found.", 404)
    return interview


def _ensure_active(interview: Interview) -> None:
    if interview.status != "in_progress":
        raise ServiceError("This interview is no longer in progress.", 409)


def create_interview(payload: dict[str, Any]) -> Interview:
    role = _required_text(payload, "role", maximum_length=120)
    experience_level = payload.get("experience_level", "mid-level")
    interview_type = payload.get("interview_type", "mixed")
    for field, value in (
        ("experience_level", experience_level),
        ("interview_type", interview_type),
    ):
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 40:
            raise ServiceError(f"'{field}' must be a non-empty string of at most 40 characters.")

    questions = payload.get("questions", [])
    if not isinstance(questions, list) or len(questions) > MAX_QUESTIONS:
        raise ServiceError(f"'questions' must be a list of at most {MAX_QUESTIONS} items.")
    cleaned_questions = []
    for question in questions:
        if not isinstance(question, str) or not question.strip() or len(question.strip()) > 1000:
            raise ServiceError("Each question must be a non-empty string of at most 1000 characters.")
        cleaned_questions.append(question.strip())

    interview = Interview(
        role=role,
        experience_level=experience_level.strip(),
        interview_type=interview_type.strip(),
    )
    interview.questions = [
        InterviewQuestion(position=index, text=text)
        for index, text in enumerate(cleaned_questions, start=1)
    ]
    return save(interview)


def get_interviews(status: str | None = None) -> list[Interview]:
    if status is not None and status not in ALLOWED_STATUSES:
        raise ServiceError("Invalid interview status.")
    return list_interviews(status)


def get_interview_detail(interview_id: int) -> Interview:
    return _find_interview(interview_id)


def add_question(interview_id: int, payload: dict[str, Any]) -> Interview:
    interview = _find_interview(interview_id)
    _ensure_active(interview)
    if len(interview.questions) >= MAX_QUESTIONS:
        raise ServiceError(f"An interview can have at most {MAX_QUESTIONS} questions.", 409)
    text = _required_text(payload, "text", maximum_length=1000)
    interview.questions.append(
        InterviewQuestion(position=len(interview.questions) + 1, text=text)
    )
    return save(interview)


def submit_answer(
    interview_id: int, question_id: int, payload: dict[str, Any]
) -> Interview:
    interview = _find_interview(interview_id)
    _ensure_active(interview)
    question = get_question(question_id)
    if question is None or question.interview_id != interview.id:
        raise ServiceError("Question not found for this interview.", 404)
    answer = _required_text(payload, "answer", maximum_length=20000)
    question.answer = answer
    return save(question)


def update_interview_status(interview_id: int, payload: dict[str, Any]) -> Interview:
    interview = _find_interview(interview_id)
    _ensure_active(interview)
    status = payload.get("status")
    if not isinstance(status, str) or status not in {"completed", "abandoned"}:
        raise ServiceError("'status' must be 'completed' or 'abandoned'.")
    if status == "completed":
        if not interview.questions:
            raise ServiceError("Add at least one question before completing the interview.", 409)
        if any(question.answer is None for question in interview.questions):
            raise ServiceError("Answer every question before completing the interview.", 409)
    interview.status = status
    return save(interview)


def remove_interview(interview_id: int) -> None:
    interview = _find_interview(interview_id)
    delete_interview(interview)


def rollback_session() -> None:
    db.session.rollback()