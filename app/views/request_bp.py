import os

from datetime import datetime
from flask import abort
from flask import jsonify
from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_current_user
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

from app import db
from app.models import MtnRequest
from app.models import MtnStatus
from app.models import MtnTask
from app.models import User
from app.models import Room
from app.models import Dorm
from app.models import ResInfo


request_bp = Blueprint("request", __name__)
api = Api(request_bp)


class MtnRequestData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        self.form_parser = reqparse.RequestParser()
        self.json_parser = reqparse.RequestParser()
        # * args parser
        self.args_parser.add_argument(
            "completed",
            type     = bool,
            help     = "Completed of the maintenance request",
            required = False,
            nullable = True,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the maintenance request",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the maintenance request",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        # * form parser
        self.form_parser.add_argument(
            "img",
            type     = FileStorage,
            help     = "Image file of the Maintenance request",
            required = True,
            nullable = False,
            location = "files",
            trim     = False,
        )
        self.form_parser.add_argument(
            "detail",
            type     = str,
            help     = "Detail of the Maintenance request",
            required = True,
            nullable = False,
            location = "form",
            trim     = False,
        )
        self.form_parser.add_argument(
            "ert",
            type     = str,
            help     = "Expected repair time of the Maintenance request",
            required = True,
            nullable = False,
            location = "form",
            trim     = False,
        )
        # * json parser
        self.json_parser.add_argument(
            "score",
            type     = int,
            help     = "Score of the Maintenance request",
            required = True,
            nullable = False,
            location = "json",
            trim     = False,
        )
        self.json_parser.add_argument(
            "feedback",
            type     = str,
            help     = "Feedback of the Maintenance request",
            required = False,
            nullable = True,
            location = "json",
            trim     = False,
        )

    # * GET /request/users/<int:user_id>/mtn_request?page=<int>&pagesize=<int>&completed=<boolean>
    @jwt_required()
    def get(self, user_id):
        current_user = get_current_user()
        if current_user.role_id != 4 or current_user.id != user_id:
            abort(403)

        args         = self.args_parser.parse_args()
        completed    = args.get("completed")
        page         = args.get("page")
        pagesize     = args.get("pagesize")
        mtn_requests = None
        
        if completed is None:
            mtn_requests = MtnRequest.query.filter_by(resident_id=user_id).paginate(page=page, per_page=pagesize)
        else:
            mtn_requests = MtnRequest.query.filter_by(resident_id=user_id, completed=completed).paginate(page=page, per_page=pagesize)
        return jsonify(
            data        = [mtn_request.to_dict() for mtn_request in mtn_requests] if mtn_requests else None,
            status_code = 200,
        )

    # * POST /request/users/<int:user_id>/mtn_request
    @jwt_required()
    def post(self, user_id):
        current_user = get_current_user()
        if current_user.role_id != 4 or current_user.id != user_id:
            abort(403)

        args   = self.form_parser.parse_args()
        img    = args.get("img")
        detail = args.get("detail")
        ert    = args.get("ert")
        img_suffix = None

        for suffix in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".apng"}:
            if img.filename.endswith(suffix):
                img_suffix = suffix
                break
        if any([not img_suffix, img.filename == "", len(img.read()) > int(os.getenv("MAX_ALLOWED_SIZE", 5242880))]):
            abort(400)

        img_dir = os.path.join(
            *os.getenv("IMG_DIR", "/etc").split("/"),
            "orgs",
            str(current_user.org_id),
            "user",
            str(current_user.id),
        )

        # ! 图片保存路径需要适配操作系统
        if os.name == "nt":
            img_dir = img_dir.replace(":", ":\\")

        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.join(img_dir, img.filename)
        img.seek(0)
        img.save(img_path)

        # * mtn_request
        mtn_request = MtnRequest(
            detail      = detail,
            img_url     = img_path,
            resident_id = current_user.id,
            ert         = datetime.strptime(ert, "%Y-%m-%d %H:%M:%S"),
        )
        db.session.add(mtn_request)
        db.session.commit()
        
        return jsonify(
            data        = mtn_request.to_dict(),
            status_code = 201,
        )

    # * PATCH /request/users/<int:user_id>/mtn_request/<int:mtn_request_id>
    @jwt_required()
    def patch(self, user_id, mtn_request_id):
        current_user = get_current_user()
        if current_user.role_id != 4 or current_user.id != user_id:
            abort(403)

        args        = self.json_parser.parse_args()
        feedback    = args.get("feedback")
        score       = args.get("score")
        mtn_request = MtnRequest.query.filter_by(completed=1, id=mtn_request_id).first_or_404()
        if not any([feedback, score]):
            abort(400)
        if feedback:
            mtn_request.feedback = feedback.strip()
        if score:
            mtn_request.score = score
        db.session.commit()
        return jsonify(
            data        = mtn_request.to_dict(),
            status_code = 200,
        )


class MtnStatusData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * args parser
        ...

    # * GET /request/users/<int:user_id>/mtn_requests/<int:mtn_request_id>/mtn_statuses
    @jwt_required()
    def get(self, user_id: int, mtn_request_id: int):
        current_user   = get_current_user()
        if current_user.role_id != 4 or current_user.id != user_id:
            abort(403)

        mtn_request  = MtnRequest.query.filter_by(resident_id=user_id, id=mtn_request_id).first_or_404()
        res_info     = ResInfo.query.filter_by(resident_id=user_id).first_or_404()
        room         = Room.query.filter_by(id=res_info.room_id).first_or_404()
        dorm         = Dorm.query.filter_by(id=room.dorm_id).first_or_404()
        mtn_task     = MtnTask.query.filter_by(mtn_request_id=mtn_request_id).one_or_none()
        mtn_tech     = None
        dorm_admin   = None
        mtn_statuses = None

        if mtn_task:
            mtn_tech     = User.query.get_or_404(mtn_task.mtn_tech_id)
            dorm_admin   = User.query.get_or_404(mtn_task.dorm_admin_id)
            mtn_statuses = MtnStatus.query.filter_by(mtn_task_id=mtn_task.id).all()
        
        return jsonify(
            data = dict(
                mtn_request  = mtn_request.to_dict(),
                res_info     = res_info.to_dict(),
                room         = room.to_dict(),
                dorm         = dorm.to_dict(),
                mtn_task     = mtn_task.to_dict(),
                mtn_tech     = mtn_tech.to_dict(),
                resident     = current_user.to_dict(),
                dorm_admin   = dorm_admin.to_dict(),
                mtn_statuses = [mtn_status.to_dict() for mtn_status in mtn_statuses] if mtn_statuses else None,
            ),
            status_code = 200,
        )   


api.add_resource(
    MtnRequestData,
    "/request/users/<int:user_id>/mtn_requests",
    "/request/users/<int:user_id>/mtn_requests/<int:mtn_request_id>",
)
api.add_resource(
    MtnStatusData,
    "/request/users/<int:user_id>/mtn_requests/<int:mtn_request_id>/mtn_statuses",
    "/request/users/<int:user_id>/mtn_requests/<int:mtn_request_id>/mtn_statuses",
)