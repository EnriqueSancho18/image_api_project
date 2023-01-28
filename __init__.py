from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register blueprints

    from . import views
    app.register_blueprint(views.bp1)
    app.register_blueprint(views.bp2)
    app.register_blueprint(views.bp3)

    return app