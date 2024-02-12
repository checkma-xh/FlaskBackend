from flask import abort
from flask import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy import collate
from sqlalchemy import and_

from app import db
from app.models import Org
from app.models import User


control_bp = Blueprint("org", __name__)
api = Api(control_bp)


class OrgData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        self.json_parser = reqparse.RequestParser()
        # * args_parser
        self.args_parser.add_argument(
            "name",
            type     = str,
            help     = "Name of the organize",
            required = False,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the organize",
            required = False,
            nullable = False,
            location = "args",
            trim     = False,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the organize",
            required = False,
            nullable = False,
            location = "args",
            trim     = False,
        )
        # * josn_parser
        self.json_parser.add_argument(
            "name",
            type     = str,
            help     = "Name of the organize",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )
        self.json_parser.add_argument(
            "detail",
            type     = str,
            help     = "Detail of the organize",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )

    # * GET /control/orgs?page=<int>&pagesize=<int>&name=<string>
    @jwt_required()
    def get(self):
        if get_jwt_identity() != 1:
            abort(403)

        args     = self.args_parser.parse_args()
        name     = args.get("name")
        page     = args.get("page")
        pagesize = args.get("pagesize")

        if name:
            org = Org.query.filter(and_(collate(Org.name, "utf8mb4_bin")==name, Org.name!="system")).first_or_404()
            return jsonify(
                data        = org.to_dict(),
                status_code = 200,
            )
        elif all([page, pagesize]):
            orgs = Org.query.filter(Org.id!=1).paginate(page=page, per_page=pagesize)
            return jsonify(
                data        = [org.to_dict() for org in orgs] if orgs else None,
                status_code = 200,
            )
        else:
            abort(400)

    # * POST /control/orgs
    @jwt_required()
    def post(self):
        if get_jwt_identity() != 1:
            abort(403)

        args    = self.json_parser.parse_args()
        detail  = args.get("detail")
        name    = args.get("name")

        if Org.query.filter(collate(Org.name, "utf8mb4_bin")==name).first():
            abort(409)

        org = Org(detail=detail, name=name)
        db.session.add(org)
        db.session.commit()

        return jsonify(
            data        = org.to_dict(),
            status_code = 201,
        )

    # * PATCH /control/orgs/<int:org_id>
    @jwt_required()
    def patch(self, org_id: int):
        if get_jwt_identity() != 1 or org_id == 1:
            abort(403)

        args     = self.json_parser.parse_args()
        detail   = args.get("detail")
        new_name = args.get("name")
        org      = Org.query.get_or_404(org_id)
        old_name = org.name

        if detail:
            org.detail = detail
        if new_name!=old_name and not Org.query.filter(collate(Org.name, "utf8mb4_bin")==new_name).one_or_none():
            org.name = new_name
        db.session.commit()
        return jsonify(
            data        = org.to_dict(),
            status_code = 200,
        )

    # * DELETE /control/orgs/<int:org_id>
    @jwt_required()
    def delete(self, org_id: int):
        if get_jwt_identity() != 1 or org_id == 1:
            abort(403)

        org = Org.query.get_or_404(org_id)
        db.session.delete(org)
        db.session.commit()
        return jsonify(status_code = 204)


class OrgAdminData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        self.json_parser = reqparse.RequestParser()
        # * args parser
        self.args_parser.add_argument(
            "account",
            type     = int,
            help     = "Account of the user",
            required = False,
            nullable = True,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the user",
            required = True,
            nullable = False,
            location = "args",
            trim     = False,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the user",
            required = True,
            nullable = False,
            location = "args",
            trim     = False,
        )
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
            "name",
            type     = str,
            help     = "Name of the user",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )
        self.json_parser.add_argument(
            "phone",
            type     = str,
            help     = "Phone of the user",
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

    # * GET /control/orgs/<int:org_id>/users?page=<int>&pagesize=<int>&account=<int>
    @jwt_required()
    def get(self, org_id: int):
        if get_jwt_identity() != 1 or org_id == 1:
            abort(403)

        args     = self.args_parser.parse_args()
        account  = args.get("account")
        page     = args.get("page")
        pagesize = args.get("pagesize")

        if account:
            org_admin = User.query.filter_by(role_id=2, org_id=org_id, account=account).first_or_404()
            return jsonify(
                data        = org_admin.to_dict(),
                status_code = 200,
            )
        elif all([page, pagesize]):
            org_admins = User.query.filter_by(role_id=2, org_id=org_id).paginate(page=page, per_page=pagesize)
            return jsonify(
                data        = [org_admin.to_dict() for org_admin in org_admins] if org_admins else None,
                status_code = 200,
            )
        else:
            abort(400)

    # * POST /control/orgs/<int:org_id>/users
    @jwt_required()
    def post(self, org_id: int):
        if get_jwt_identity() != 1 or org_id == 1:
            abort(403)

        args      = self.json_parser.parse_args()
        org_admin = User(
                account = args.get("account"),
                name    = args.get("name"),
                org_id  = org_id,
                phone   = args.get("phone"),
                role_id = 2,                   
            )
        org_admin.set_pwd(args.get("pwd"))
        db.session.add(org_admin)
        db.session.commit()
        return jsonify(
            data        = org_admin.to_dict(),
            status_code = 201,
        )

    # * DELETE /control/orgs/<int:org_id>/users/<int:user_id>
    @jwt_required()
    def delete(self, org_id: int, user_id: int):
        if get_jwt_identity() != 1 or org_id == 1:
            abort(403)

        org_admin = User.query.filter_by(role_id=2, id=user_id, org_id=org_id).first_or_404()
        db.session.delete(org_admin)
        db.session.commit()
        return jsonify(status_code = 204)


api.add_resource(OrgData, "/control/orgs", "/control/orgs/<int:org_id>")
api.add_resource(
    OrgAdminData,
    "/control/orgs/<int:org_id>/users",
    "/control/orgs/<int:org_id>/users/<int:user_id>",
)