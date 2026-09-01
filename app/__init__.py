from flask import Flask
from .database import initialize_database
from .routes import dashboard_blueprint


def create_app(test_config=None):
    application = Flask(__name__)
    application.config.from_mapping(
        DATABASE_PATH="network_monitor.db",
        SECRET_KEY="local-network-monitor",
        MAX_PACKET_ROWS=10000,
    )
    if test_config:
        application.config.update(test_config)
    initialize_database(application.config["DATABASE_PATH"])
    application.register_blueprint(dashboard_blueprint)
    return application

