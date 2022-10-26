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

print(1)
import oracledb
from sqlalchemy import create_engine
import sys
import os
oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb
import cx_Oracle

print(2)
    
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    print('hii')
        
    # if sys.platform.startswith("darwin"):
    #     oracledb.init_oracle_client(
    #         lib_dir=os.environ.get("HOME")+"/Downloads/instantclient_19_8",
    #         config_dir="")
    # elif sys.platform.startswith("win"):
    #     oracledb.init_oracle_client(
    #         lib_dir=r"C:\\Program Files\\Oracle\\instantclient_21_7")
    #     print('got the file')
    # else assume system library search path includes Oracle Client libraries
    # On Linux, use ldconfig or set LD_LIBRARY_PATH, as described in installation documentation.

    oracledb.init_oracle_client(
        lib_dir=os.environ.get("HOME")+"/instantclient_21_7",
        config_dir="")

    username = "admin"
    # set the password in an environment variable called "MYPW" for security
    password = 'Nulifendou8!'
    dsn = "modernfoodiedb_high"

    engine = create_engine(
        f'oracle://{username}:{password}@{dsn}/?encoding=UTF-8&nencoding=UTF-8', max_identifier_length=128)

    with engine.connect() as conn:
        print('connect success')
        print(conn.scalar("select sysdate from dual"))
        
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

    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE')
        response.headers.set('Access-Control-Allow-Headers', '*')
    
        return response
    
    return app

print(3)

# Create all models, but generated tables does not setup foreign keys properly
# db.create_all(app=create_app())
