from datetime import timedelta
from flask import Blueprint
from flask import abort
from flask import jsonify
from flask_restful import reqparse
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import jwt_required
from flask_restful import Api
from flask_restful import Resource

from app.models import User


auth_bp = Blueprint("auth", __name__)
api = Api(auth_bp)


class Login(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.json_parser = reqparse.RequestParser()
        # * json parser
        self.json_parser.add_argument(
            "account",
            type     = int,
            help     = "Account of the user",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )
        self.json_parser.add_argument(
            "pwd",
            type     = str,
            help     = "Password of the user",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )

    # * POST /auth/login
    def post(self):
        args = self.json_parser.parse_args()
        current_user = User.query.filter_by(account=args.get("account")).first_or_404()
        if not current_user.validate_pwd(args.get("pwd")):
            abort(401)
        
        return jsonify(
            access_token  = create_access_token(identity=current_user.id),
            refresh_token = create_refresh_token(identity=current_user.id),
            status_code   = 200,
        )


class Refresh(Resource):
    # * POST /auth/refresh
    @jwt_required(refresh=True)
    def post(self):
        return jsonify(
            access_token = create_access_token(identity=get_jwt_identity()),
            status_code  = 200,
        )


class Logout(Resource):
    # * POST /auth/logout
    @jwt_required()
    def post(self):
        """
        使用 JWT 的登出功能可以有 3 种方法
        1. 前端删除 token;
        2. 向后端请求有效时长接近 0 的 token 并更新 token;
        3. 后端维护 token 黑名单;
        4. 修改 SECRET_KEY, 对所有用户 token 生效;
        这里选择第 3 种方式, 不维护黑名单能够减少系统负担
        """
        return jsonify(
            access_token  = create_access_token(identity=get_jwt_identity(), expires_delta=timedelta(microseconds=1)),
            refresh_token = create_refresh_token(identity=get_jwt_identity(), expires_delta=timedelta(microseconds=1)),
            status_code   = 200,
        )


api.add_resource(Login, "/auth/login")
api.add_resource(Refresh, "/auth/refresh")
api.add_resource(Logout, "/auth/logout")