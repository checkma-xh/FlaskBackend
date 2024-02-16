from sqlalchemy import and_
from flask import jsonify
from flask import Blueprint
from flask import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_current_user
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse

from app import db
from app.models import MtnRequest
from app.models import MtnStatus
from app.models import MtnTask
from app.models import User
from app.models import Room
from app.models import Dorm
from app.models import ResInfo
from app.models import DormManager
from app.models import DormMtnManager


assign_bp = Blueprint("assign", __name__)
api = Api(assign_bp)

 
class MtnRequestData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
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
            "mtn_tech_id",
            type     = int,
            help     = "ID of the maintenance worker",
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

    # * GET /assign/dorm/<int:dorm_id>/mtn_requests?page=<int>&pagesize=<int>&completed=<boolean>&mtn_tech_id=<int>
    @jwt_required()
    def get(self, dorm_id):
        current_user = get_current_user()
        if current_user.role_id != 3:
            abort(403)

        dorm_manager = DormManager.query.filter_by(dorm_admin_id=current_user.id, dorm_id=dorm_id).first_or_404()
        args         = self.args_parser.parse_args()
        completed    = args.get("completed")
        mtn_tech_id  = args.get("mtn_tech_id")
        page         = args.get("page")
        pagesize     = args.get("pagesize")
        mtn_requests = None

        mtn_requests = db.session.query(MtnRequest).\
            join(ResInfo, ResInfo.resident_id == MtnRequest.resident_id).\
            join(Room, Room.id == ResInfo.room_id).\
            join(Dorm, Dorm.id == Room.dorm_id).filter(Dorm.id == dorm_id)
        
        if completed is None:
            if mtn_tech_id is None:
                mtn_requests = mtn_requests.paginate(page=page, per_page=pagesize)
            else:
                mtn_requests = mtn_requests.\
                    join(MtnTask, MtnTask.mtn_request_id == MtnRequest.id).\
                    filter(MtnTask.mtn_tech_id == mtn_tech_id).\
                    paginate(page=page, per_page=pagesize)
        else:
            if mtn_tech_id is None:
                mtn_requests = mtn_requests.\
                    filter(Dorm.id == dorm_id).\
                    filter(MtnRequest.completed == completed).\
                    paginate(page=page, per_page=pagesize)
            else:
                mtn_requests = mtn_requests.\
                    join(MtnTask, MtnTask.mtn_request_id == MtnRequest.id).\
                    filter(Dorm.id == dorm_id).\
                    filter(MtnRequest.completed == completed).\
                    filter(MtnTask.mtn_tech_id == mtn_tech_id).\
                    paginate(page=page, per_page=pagesize)
        return jsonify(
            data        = [mtn_request.to_dict() for mtn_request in mtn_requests] if mtn_requests else None,
            status_code = 200,
        )


class MtnStatusData(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * args parser
        ...

    # * GET /assign/dorm/<int:dorm_id>/mtn_requests/<int:mtn_request_id>/mtn_statuses
    @jwt_required()
    def get(self, dorm_id: int, mtn_request_id: int):
        current_user   = get_current_user()
        if current_user.role_id != 3:
            abort(403)
        dorm_manager = DormManager.query.filter_by(dorm_admin_id=current_user.id, dorm_id=dorm_id).first_or_404()
        mtn_request  = MtnRequest.query.get_or_404(mtn_request_id)
        res_info     = ResInfo.query.filter_by(resident_id=mtn_request.resident_id).first_or_404()
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
                resident     = User.query.get_or_404(mtn_request.resident_id).to_dict(),
                dorm_admin   = dorm_admin.to_dict(),
                mtn_statuses = [mtn_status.to_dict() for mtn_status in mtn_statuses] if mtn_statuses else None,
            ),
            status_code = 200,
        )   


class MtnTechData(Resource):
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * args parser
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the maintenance worker",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the maintenance worker",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )

    # * GET /assign/dorm/<int:dorm_id>/users
    @jwt_required()
    def get(self, dorm_id):
        current_user = get_current_user()
        if current_user.role_id != 3:
            abort(403)
        
        args         = self.args_parser.parse_args()
        page         = args.get("page")
        pagesize     = args.get("pagesize")
        dorm_manager = DormManager.query.filter_by(dorm_admin_id=current_user.id, dorm_id=dorm_id).first_or_404()
        mtn_techs    = db.session.query(User).\
            join(DormMtnManager, DormMtnManager.mtn_tech_id == User.id).\
            filter(DormMtnManager.dorm_id == dorm_id).\
            paginate(page=page, per_page=pagesize)
        return jsonify(
            data        = [mtn_tech.to_dict() for mtn_tech in mtn_techs] if mtn_techs else None,
            status_code = 200,
        )


class MtnTaskData(Resource):
    def __init__(self):
        self.json_parser = reqparse.RequestParser()
        self.json_parser.add_argument(
            "dorm_admin_id",
            type     = int,
            help     = "ID of the dormitory admin",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )
        self.json_parser.add_argument(
            "mtn_tech_id",
            type     = int,
            help     = "ID of the maintenance worker",
            required = True,
            nullable = False,
            location = "json",
            trim     = True,
        )


    # * POST /assign/dorm/<int:dorm_id>/mtn_requests/<int:mtn_request_id>/mtn_tasks
    @jwt_required()
    def post(self, dorm_id: int, mtn_request_id: int):
        current_user = get_current_user()
        if current_user.role_id != 3:
            abort(403)

        if MtnTask.query.filter_by(mtn_request_id=mtn_request_id).first():
            abort(409)

        dorm_manager = DormManager.query.filter_by(dorm_admin_id=current_user.id, dorm_id=dorm_id).first_or_404()
        dorm = db.session.query(Dorm).\
            join(Room, Room.dorm_id == Dorm.id).\
            join(ResInfo, ResInfo.room_id == Room.id).\
            join(User, User.id == ResInfo.resident_id).\
            join(MtnRequest, MtnRequest.resident_id == User.id).\
            filter(and_(MtnRequest.id == mtn_request_id, Dorm.id == dorm_id)).first_or_404()

        args     = self.json_parser.parse_args()
        mtn_task = MtnTask(
            dorm_admin_id  = args.get("dorm_admin_id"),
            mtn_request_id = mtn_request_id,
            mtn_tech_id    = args.get("mtn_tech_id"),
        )
        db.session.add(mtn_task)
        db.session.commit()
        return jsonify(
            data        = mtn_task.to_dict(),
            status_code = 200,
        )


class DormManagerData(Resource):
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * parser
        ...

    # * GET /assign/users/<int:user_id>/dorm_manager
    @jwt_required()
    def get(self, user_id: int):
        current_user = get_current_user()
        if current_user.role_id != 3 or current_user.id != user_id:
            abort(403)

        dorm_manager = DormManager.query.filter_by(dorm_admin_id=user_id).first_or_404()
        return jsonify(
            data        = dorm_manager.to_dict(),
            status_code = 200,
        )
        

api.add_resource(
    MtnRequestData,
    "/assign/dorm/<int:dorm_id>/mtn_requests",
    "/assign/dorm/<int:dorm_id>/mtn_requests",
)
api.add_resource(
    MtnStatusData,
    "/assign/dorm/<int:dorm_id>/mtn_requests/<int:mtn_request_id>/mtn_statuses",
    "/assign/dorm/<int:dorm_id>/mtn_requests/<int:mtn_request_id>/mtn_statuses",
)
api.add_resource(
    MtnTechData,
    "/assign/dorm/<int:dorm_id>/users",
    "/assign/dorm/<int:dorm_id>/users",
)
api.add_resource(
    MtnTaskData,
    "/assign/dorm/<int:dorm_id>/mtn_requests/<int:mtn_request_id>/mtn_tasks",
    "/assign/dorm/<int:dorm_id>/mtn_requests/<int:mtn_request_id>/mtn_tasks",
)
api.add_resource(
    DormManagerData,
    "/assign/users/<int:user_id>/dorm_manager",
    "/assign/users/<int:user_id>/dorm_manager",
)