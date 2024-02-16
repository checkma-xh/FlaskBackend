from datetime import datetime
from flask import jsonify
from flask import Blueprint
from flask import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_current_user
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse
from sqlalchemy import case

from app import db
from app.models import MtnRequest
from app.models import User
from app.models import MtnTask
from app.models import Room
from app.models import Dorm
from app.models import ResInfo
from app.models.org import Org


data_analysis_bp = Blueprint("data_analysis", __name__)
api = Api(data_analysis_bp)


class RoomDataAnalysis(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * args parser
        self.args_parser.add_argument(
            "start_time",
            type     = str,
            help     = "Start time of repair for data analysis",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "end_time",
            type     = str,
            help     = "End time of repair for data analysis",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "ASC",
            type     = bool,
            help     = "Sort in positive order",
            required = False,
            nullable = True,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "sort_field",
            type     = str,
            help     = "Fields to sort on",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the data",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the data",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
    
    # * GET /data_analysis/orgs/<int:org_id>/dorm/<int:dorm_id>/rooms?page=<int>&pagesize=<int>start_time=<str>&end_time=<str>&ASC=<boolean>&sort_field=<str>
    @jwt_required()
    def get(self, org_id: int, dorm_id: int):
        current_user = get_current_user()
        dorm = Dorm.query.filter_by(org_id=org_id, id=dorm_id).one_or_none()
        if not all([current_user.role_id == 2, current_user.org_id == org_id, dorm != None]):
            abort(403)

        args       = self.args_parser.parse_args()
        start_time = args.get("start_time")
        end_time   = args.get("end_time")
        ASC        = args.get("ASC")
        sort_field = args.get("sort_field")
        page       = args.get("page")
        pagesize   = args.get("pagesize")

        query_result = db.session.query(
            db.func.count(MtnRequest.request_time).label("mtn_request_count"),
            Room.id,
            Room.room_num,
        )\
        .outerjoin(ResInfo, ResInfo.room_id == Room.id)\
        .outerjoin(MtnRequest, MtnRequest.resident_id == ResInfo.resident_id)\
        .filter(Room.dorm_id == dorm_id)\
        .filter(MtnRequest.request_time.between(
            datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        ))\
        .group_by(Room.id, Room.room_num)

        if sort_field == "mtn_request_count":
            if ASC != None:
                query_result = query_result.order_by(db.func.count(Room.id).asc())
            else:
                query_result = query_result.order_by(db.func.count(Room.id).desc())
        elif sort_field == "room_num":
            if ASC != None:
                query_result = query_result.order_by(Room.room_num.asc())
            else:
                query_result = query_result.order_by(Room.room_num.desc())
        
        query_result = query_result.paginate(page=page, per_page=pagesize)

        return jsonify(
            data        = [line._asdict() for line in query_result] if query_result else None,
            status_code = 200,
        )
    

class DormDataAnalysis(Resource):
    # * 在资源类中创建请求解析器
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * args parser
        self.args_parser.add_argument(
            "start_time",
            type     = str,
            help     = "Start time of repair for data analysis",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "end_time",
            type     = str,
            help     = "End time of repair for data analysis",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "ASC",
            type     = bool,
            help     = "Sort in positive order",
            required = False,
            nullable = True,
            location = "args",
            trim     = True,
        )
        # self.args_parser.add_argument(
        #     "sort_field",
        #     type     = str,
        #     help     = "Fields to sort on",
        #     required = True,
        #     nullable = False,
        #     location = "args",
        #     trim     = True,
        # )
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the data",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the data",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )

    # * GET /data_analysis/orgs/<int:org_id>/dorms?page=<int>&pagesize=<int>start_time=<str>&end_time=<str>&ASC=<boolean>
    @jwt_required()
    def get(self, org_id: int):
        current_user = get_current_user()
        if not all([current_user.role_id == 2, current_user.org_id == org_id]):
            abort(403)

        args       = self.args_parser.parse_args()
        start_time = args.get("start_time")
        end_time   = args.get("end_time")
        ASC        = args.get("ASC")
        # sort_field = args.get("sort_field")
        page       = args.get("page")
        pagesize   = args.get("pagesize")

        query_result = db.session.query(
            db.func.count(Dorm.id).label("mtn_request_count"),
            Dorm.id,
            Dorm.name,
        )\
        .outerjoin(Room, Room.dorm_id == Dorm.id)\
        .outerjoin(ResInfo, ResInfo.room_id == Room.id)\
        .outerjoin(MtnRequest, MtnRequest.resident_id == ResInfo.resident_id)\
        .outerjoin(Org, Org.id == Dorm.org_id)\
        .filter(Org.id == org_id)\
        .filter(MtnRequest.request_time.between(
            datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        ))\
        .group_by(Dorm.id, Dorm.name)

        if ASC != None:
            query_result = query_result.order_by(db.func.count(Dorm.id).asc())
        else:
            query_result = query_result.order_by(db.func.count(Dorm.id).desc())

        # if sort_field == ...:
        #     if ASC != None:
        #         query_result = query_result.order_by(....asc())
        #     else:
        #         query_result = query_result.order_by(....desc())
        # elif sort_field == ...:
        #     ...
        
        query_result = query_result.paginate(page=page, per_page=pagesize)

        return jsonify(
            data        = [line._asdict() for line in query_result] if query_result else None,
            status_code = 200,
        )


class TechMtnCount(Resource):
    def __init__(self):
        self.args_parser = reqparse.RequestParser()
        # * args parser
        self.args_parser.add_argument(
            "start_time",
            type     = str,
            help     = "Start time of repair for data analysis",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "end_time",
            type     = str,
            help     = "End time of repair for data analysis",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "ASC",
            type     = bool,
            help     = "Sort in positive order",
            required = False,
            nullable = True,
            location = "args",
            trim     = True,
        )
        # self.args_parser.add_argument(
        #     "sort_field",
        #     type     = str,
        #     help     = "Fields to sort on",
        #     required = True,
        #     nullable = False,
        #     location = "args",
        #     trim     = True,
        # )
        self.args_parser.add_argument(
            "page",
            type     = int,
            help     = "Page of the data",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )
        self.args_parser.add_argument(
            "pagesize",
            type     = int,
            help     = "Pagesize of the data",
            required = True,
            nullable = False,
            location = "args",
            trim     = True,
        )

    # * GET /data_analysis/orgs/<int:org_id>/users?page=<int>&pagesize=<int>start_time=<str>&end_time=<str>&ASC=<boolean>
    @jwt_required()
    def get(self, org_id: int):
        current_user = get_current_user()
        if not all([current_user.role_id == 2, current_user.org_id == org_id]):
            abort(403)

        args       = self.args_parser.parse_args()
        start_time = args.get("start_time")
        end_time   = args.get("end_time")
        ASC        = args.get("ASC")
        # sort_field = args.get("sort_field")
        page       = args.get("page")
        pagesize   = args.get("pagesize")

        query_result = db.session.query(
            User.id,
            db.func.sum(MtnRequest.score).label("total_score"),
            db.func.sum(case((MtnRequest.completed == True, 1), else_=0)).label("completed_true_count"),
            db.func.sum(case((MtnRequest.score != None, 1), else_=0)).label("number_raters"),
            db.func.sum(case((MtnRequest.completed == False, 1), else_=0)).label("completed_false_count"),
        )\
        .outerjoin(MtnTask, MtnTask.mtn_tech_id == User.id)\
        .outerjoin(MtnRequest, MtnRequest.id == MtnTask.mtn_request_id)\
        .filter(MtnRequest.request_time.between(
            datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        ))\
        .filter(User.org_id == org_id)\
        .filter(User.role_id == 5)\
        .group_by(User.id)

        if ASC != None:
            query_result = query_result.order_by(db.func.count(User.id).asc())
        else:
            query_result = query_result.order_by(db.func.count(User.id).desc())

        # if sort_field == ...:
        #     if ASC != None:
        #         query_result = query_result.order_by(....asc())
        #     else:
        #         query_result = query_result.order_by(....desc())
        # elif sort_field == ...:
        #     ...
        
        query_result = query_result.paginate(page=page, per_page=pagesize)
        
        return jsonify(
            data        = [line._asdict() for line in query_result] if query_result else None,
            status_code = 200,
        )


api.add_resource(
    RoomDataAnalysis,
    "/data_analysis/orgs/<int:org_id>/dorm/<int:dorm_id>/rooms",
    "/data_analysis/orgs/<int:org_id>/dorm/<int:dorm_id>/rooms",
)
api.add_resource(
    DormDataAnalysis,
    "/data_analysis/orgs/<int:org_id>/dorms",
    "/data_analysis/orgs/<int:org_id>/dorms",
)
api.add_resource(
    TechMtnCount,
    "/data_analysis/orgs/<int:org_id>/users",
    "/data_analysis/orgs/<int:org_id>/users",
)
