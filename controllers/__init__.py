from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from ..extentions import db
from ..services import (
    ServiceError,
    add_question,
    create_interview,
    get_interview_detail,
    get_interviews,
    remove_interview,
    rollback_session,
    submit_answer,
    update_interview_status,
)

api = Blueprint("api", __name__, url_prefix="/api")


def _json_body() -> dict:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ServiceError("Request body must be a JSON object.")
    return payload


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.get("/ready")
def readiness():
    db.session.execute(text("SELECT 1"))
    return jsonify({"status": "ready"})


@api.get("/interviews")
def list_interview_route():
    status = request.args.get("status")
    return jsonify({"interviews": [item.to_dict() for item in get_interviews(status)]})


@api.post("/interviews")
def create_interview_route():
    interview = create_interview(_json_body())
    return jsonify({"interview": interview.to_dict()}), 201


@api.get("/interviews/<int:interview_id>")
def get_interview_route(interview_id: int):
    return jsonify({"interview": get_interview_detail(interview_id).to_dict()})


@api.patch("/interviews/<int:interview_id>")
def update_interview_route(interview_id: int):
    interview = update_interview_status(interview_id, _json_body())
    return jsonify({"interview": interview.to_dict()})


@api.delete("/interviews/<int:interview_id>")
def delete_interview_route(interview_id: int):
    remove_interview(interview_id)
    return "", 204


@api.post("/interviews/<int:interview_id>/questions")
def add_question_route(interview_id: int):
    interview = add_question(interview_id, _json_body())
    return jsonify({"interview": interview.to_dict()}), 201


@api.patch("/interviews/<int:interview_id>/questions/<int:question_id>")
def submit_answer_route(interview_id: int, question_id: int):
    interview = submit_answer(interview_id, question_id, _json_body())
    return jsonify({"interview": interview.to_dict()})


@api.errorhandler(ServiceError)
def handle_service_error(error: ServiceError):
    return jsonify({"error": str(error)}), error.status_code


@api.errorhandler(HTTPException)
def handle_http_error(error: HTTPException):
    return jsonify({"error": error.description}), error.code


@api.errorhandler(SQLAlchemyError)
def handle_database_error(error: SQLAlchemyError):
    rollback_session()
    current_app.logger.exception("Database request failed", exc_info=error)
    return jsonify({"error": "A database error occurred."}), 500