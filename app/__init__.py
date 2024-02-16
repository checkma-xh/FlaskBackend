from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
# from flask_celery import Celery
# from flask_redis import FlaskRedis
from flask_restful import Api
from flask_cors import CORS

from .settings import Config


# * 创建实例
db     = SQLAlchemy()
jwt    = JWTManager()
api    = Api()
# celery = Celery()
# redis  = FlaskRedis()
app    = Flask(__name__)
app.config.from_object(Config)

# * 更改实例
db.init_app(app)
jwt.init_app(app)
api.init_app(app)
# celery.init_app(app)
# redis.init_app(app)

# * 自定义跨域
CORS(app, resources={r"/*": {"origins": "*"}})


# todo 设置 get_current_user 回调函数
from app.models import User

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get_or_404(identity)


# * 注册蓝图
from .views import assign_bp
from .views import auth_bp
from .views import control_bp
from .views import data_analysis_bp
from .views import exec_bp
# from .views import org_data_bp
from .views import request_bp
from .views import userinfo_bp


app.register_blueprint(assign_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(control_bp)
app.register_blueprint(data_analysis_bp)
app.register_blueprint(exec_bp)
# app.register_blueprint(org_data_bp)
app.register_blueprint(request_bp)
app.register_blueprint(userinfo_bp)


from .commands import init_db
from .commands import seed_db