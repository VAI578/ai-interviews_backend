from pathlib import Path

from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

from .config import Config
from .extentions import cors, db
from .models import Interview, InterviewQuestion


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from .controllers import api
    app.register_blueprint(api)

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create the database tables."""
        try:
            db.metadata.create_all(
                bind=db.engine,
                tables=[Interview.__table__, InterviewQuestion.__table__],
            )
        except SQLAlchemyError:
            app.logger.exception("Unable to initialize the database")
            raise
        print("Database tables created.")

    @app.get("/")
    def index():
        return {"name": "AI Interview API", "health": "/api/health"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=app.config.get("PORT", 5000))