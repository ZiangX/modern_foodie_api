import sentry_sdk
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
from flask_mail import Mail
from sentry_sdk.integrations.flask import FlaskIntegration

from ecommerce_blueprint_version.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
# login_manager.login_message_category = 'info'
mail = Mail()


# Add error logging tools
# sentry_sdk.init(
#     dsn="https://d6f275ba557c461eb46cea97882583cb@o1094374.ingest.sentry.io/6113391",
#     integrations=[FlaskIntegration()],

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0
# )


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    # login_manager.init_app(app)
    mail.init_app(app)

    from ecommerce_blueprint_version.users.routes import users
    from ecommerce_blueprint_version.products.routes import products
    from ecommerce_blueprint_version.categories.routes import categories
    from ecommerce_blueprint_version.orders.routes import orders
    from ecommerce_blueprint_version.main.routes import main
    from ecommerce_blueprint_version.auth.routes import auth
    from ecommerce_blueprint_version.communication.routes import communication
    # from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(products)
    app.register_blueprint(categories)
    app.register_blueprint(orders)
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(communication)
    # app.register_blueprint(errors)

    @app.after_request
    def after_request(response):
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE')
        response.headers.set('Access-Control-Allow-Headers', '*')
    
        return response
    
    return app

# Create all models, but generated tables does not setup foreign keys properly
# db.create_all(app=create_app())
