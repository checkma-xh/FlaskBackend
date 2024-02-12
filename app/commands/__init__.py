from app.models import DormManager
from app.models import DormMtnManager
from app.models import Dorm
from app.models import MtnRequest
from app.models import MtnStatus
from app.models import MtnTask
from app.models import Org
from app.models import ResInfo
from app.models import Role
from app.models import Room
from app.models import TechDetail
from app.models import User
from app import db


# ! 必须插入固定值
def insert_role():
    role_data = [
        {"id": 1, "detail": "", "name": "sys_admin"},
        {"id": 2, "detail": "", "name": "org_admin"},
        {"id": 3, "detail": "", "name": "dorm_admin"},
        {"id": 4, "detail": "", "name": "resident"},
        {"id": 5, "detail": "", "name": "mtn_tech"},
    ]
    db.session.add_all([Role(**item) for item in role_data])
    db.session.commit()


# ! 必须插入 Org(name="system"), 第一个加入系统的企业是 system
def insert_org(faker, num):
    org_names = ["system"] + [faker.company_prefix() + "大学" for _ in range(num)]
    data = [Org(**{"detail": "", "name": name}) for name in org_names]

    db.session.add_all(data)
    db.session.commit()


def new_dorm(faker, org_id):
    return Dorm(
        **{
            "name"  : faker.district() + "楼",
            "org_id": org_id,
        }
    )


def new_room(faker, dorm_id):
    return Room(**{"dorm_id": dorm_id, "room_num": faker.random_number(digits=3)})


def new_user(faker, org_id, role_id):
    user = User(
        **{
            "account": faker.random_number(digits=8),
            "name": faker.name(),
            "org_id": org_id,
            "phone": faker.phone_number(),
            "role_id": role_id,
        }
    )
    user.set_pwd("123456")
    return user


def new_tech_detail(mtn_tech_id, mtn_count):
    return TechDetail(**{"mtn_tech_id": mtn_tech_id, "mtn_count": mtn_count})


def new_res_info(room_id, resident_id):
    return ResInfo(**{"room_id": room_id, "resident_id": resident_id})


def new_dorm_mtn_manager(dorm_id, mtn_tech_id):
    return DormMtnManager(**{"dorm_id": dorm_id, "mtn_tech_id": mtn_tech_id})


def new_dorm_manager(dorm_id, dorm_admin_id):
    return DormManager(**{"dorm_id": dorm_id, "dorm_admin_id": dorm_admin_id})


def new_mtn_request(faker, resident_id):
    return MtnRequest(
        **{"detail": "", "img_url": faker.image_url(), "resident_id": resident_id}
    )


def new_mtn_task(dorm_admin_id, mtn_request_id, mtn_tech_id):
    return MtnTask(
        **{
            "dorm_admin_id" : dorm_admin_id,
            "mtn_request_id": mtn_request_id,
            "mtn_tech_id"   : mtn_tech_id,
        }
    )


def new_mtn_status(faker, mtn_task_id):
    return MtnStatus(
        **{"detail": "", "img_url": faker.image_url(), "mtn_task_id": mtn_task_id}
    )


from .seed_db import seed_db
from .init_db import init_db
