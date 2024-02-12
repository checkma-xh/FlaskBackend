from typing import Optional
from flask import abort
from flask import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_current_user
from flask_jwt_extended import jwt_required
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse

from app import db


userinfo_bp = Blueprint("userinfo", __name__)
api = Api(userinfo_bp)


class UserData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.json_parser = reqparse.RequestParser()
        # * json parser
        self.json_parser.add_argument(
            "phone",
            type     = str,
            help     = "Phone of the user",
            required = False,
            nullable = True,
            location = "json",
            trim     = True,
        )
        self.json_parser.add_argument(
            "old_pwd",
            type     = str,
            help     = "New password of the user",
            required = False,
            nullable = True,
            location = "json",
            trim     = False,
        )
        self.json_parser.add_argument(
            "new_pwd",
            type     = str,
            help     = "Old password of the user",
            required = False,
            nullable = True,
            location = "json",
            trim     = False,
        )

    # * GET /userinfo/users/<int:user_id>
    @jwt_required()
    def get(self, user_id: int):
        current_user = get_current_user()
        if current_user.id != user_id:
            abort(403)

        return jsonify(
            data         = current_user.to_dict(),
            status_coade = 200,
        )

    # * 检查电话号码格式
    def phoneformat_check(self, phone: Optional[str] = None):
        if not phone:
            return False
        if 7 <= len(phone) <= 11 and all(c.isdigit() for c in phone):
            return True
        return False

    # * 检查密码格式
    def pwdformat_check(self, pwd: Optional[str] = None):
        if not pwd:
            return False
        if not (8 <= len(pwd) <= 36):
            return False
        if not any(char.isalpha() for char in pwd):
            return False
        if not any(char.isdigit() for char in pwd):
            return False

        pwd_symbols = {char for char in pwd if not char.isalpha() and not char.isdigit()}
        char_symbols = set("""`~!@#$%^&*()_-+={}[]|\:;'",<>.?/""")

        if pwd_symbols & char_symbols != pwd_symbols:
            return False
        return True

    # * PATCH /userinfo/users/<int:user_id>
    @jwt_required()
    def patch(self, user_id: int):
        current_user = get_current_user()
        if user_id != current_user.id:
            abort(403)

        args     = self.json_parser.parse_args()
        phone    = args.get("phone")
        old_pwd  = args.get("old_pwd")
        new_pwd  = args.get("new_pwd")

        if not any([phone, old_pwd, new_pwd]):
            abort(400)
        if self.phoneformat_check(phone):
            current_user.phone = phone
        
        if not all([new_pwd, old_pwd]):
            pass
        elif all([current_user.validate_pwd(old_pwd), self.pwdformat_check(new_pwd)]):
            current_user.set_pwd(new_pwd)

        db.session.commit()
        return jsonify(
            data        = current_user.to_dict(),
            status_code = 200,
        )


api.add_resource(
    UserData, "/userinfo/users/<int:user_id>", "/userinfo/users/<int:user_id>"
)
