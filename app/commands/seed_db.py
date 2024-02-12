import click

from faker import Faker

from app import app
from app import db
from app.models import Org
from . import insert_role
from . import insert_org
from . import new_dorm
from . import new_room
from . import new_user
from . import new_tech_detail
from . import new_res_info
from . import new_dorm_mtn_manager
from . import new_dorm_manager
from . import new_mtn_request
from . import new_mtn_task
from . import new_mtn_status


# ! ORG_NUM 包括了 system
ORG_NUM       = 3
ROLE_NUM      = 5
SYS_ADMIN_NUM = ORG_NUM

# ! 此常量背景为在一个 Org 下的相关值, 一个 Dorm 对应一位 DormAdmin
ORG_ADMIN_NUM  = 1
DORM_NUM       = 4
DORM_ADMIN_NUM = DORM_NUM

# ! 此常量背景为在一个 Dorm 下的相关值
ROOM_NUM = 2

# ! 此常量背景为在一个 Room 下的相关值
RESIDENT_NUM = 2

# ! 一位房客报修的申请数量
MTN_REQUEST_NUM = 1

# ! 一个维修任务的状态更新次数, 可变, 但假数据可简化
MTN_STATUS_NUM  = 2

# ! 维修人员管理的楼栋数量, 可变, 但假数据可简化
DORM_MTN_MANAGER_NUM = 2
MTN_TECH_NUM         = DORM_NUM // DORM_MTN_MANAGER_NUM

faker = Faker(locale="zh_CN")


# todo 创建并插入数据
@app.cli.command()
def seed_db():
    insert_role()
    insert_org(faker, ORG_NUM-1)
    
    # * sys_admin
    db.session.add_all([new_user(faker, 1, 1) for _ in range(ORG_NUM)])

    # ! 先 commit 才能用数据, 否则拿到的所有对象都为空
    # * org_admin, dorm_admin, resident, mtn_tech_admin, dorm, room, tech_detail, res_info, dorm_mtn_manager, dorm_manager, mtn_request, mtn_task, mtn_status
    for org in Org.query.filter(Org.id > 1).all():
        org_admin_data  = [new_user(faker, org.id, 2) for _ in range(ORG_ADMIN_NUM)]
        dorm_admin_data = [new_user(faker, org.id, 3) for _ in range(DORM_ADMIN_NUM)]
        mtn_tech_data   = [new_user(faker, org.id, 5) for _ in range(MTN_TECH_NUM)]
        db.session.add_all(org_admin_data)
        db.session.add_all(dorm_admin_data)
        db.session.add_all(mtn_tech_data)
        db.session.commit()

        dorm_data     = [new_dorm(faker, org.id) for _ in range(DORM_NUM)]
        resident_data = [new_user(faker, org.id, 4) for _ in range(DORM_NUM*ROOM_NUM*RESIDENT_NUM)]
        db.session.add_all(dorm_data)
        db.session.add_all(resident_data)
        db.session.commit()

        room_data         = [new_room(faker, dorm.id) for dorm in dorm_data for _ in range(ROOM_NUM)]
        tech_detail_data  = [new_tech_detail(mtn_tech.id, 0) for mtn_tech in mtn_tech_data]
        mtn_request_data  = [new_mtn_request(faker, resident.id) for resident in resident_data for _ in range(MTN_REQUEST_NUM)]
        dorm_manager_data = [new_dorm_manager(dorm_data[index].id, dorm_admin_data[index].id) for index in range(DORM_NUM)]
        db.session.add_all(room_data)
        db.session.add_all(tech_detail_data)
        db.session.add_all(mtn_request_data)
        db.session.add_all(dorm_manager_data)
        db.session.commit()

        # * 浅拷贝需要 pop 的数据, 不修改原数据
        resident_data_cp      = resident_data[:]
        dorm_data_cp          = dorm_data[:]
        mtn_request_data_cp   = mtn_request_data[:]
        res_info_data         = [new_res_info(room.id, resident_data_cp.pop().id) for room in room_data for _ in range(RESIDENT_NUM)]
        dorm_mtn_manager_data = [new_dorm_mtn_manager(dorm_data_cp.pop().id, mtn_tech.id) for mtn_tech in mtn_tech_data for _ in range(DORM_MTN_MANAGER_NUM)]
        db.session.add_all(res_info_data)
        db.session.add_all(dorm_mtn_manager_data)
        db.session.commit()

        tech_dorm_admin_map = {dorm_mtn_manager.mtn_tech_id: dorm_manager.dorm_admin_id for dorm_mtn_manager in dorm_mtn_manager_data for dorm_manager in dorm_manager_data if dorm_mtn_manager.dorm_id == dorm_manager.dorm_id}
        mtn_task_data       = [new_mtn_task(tech_dorm_admin_map.get(mtn_tech.id), mtn_request_data_cp.pop().id, mtn_tech.id) for mtn_tech in mtn_tech_data for _ in range(DORM_MTN_MANAGER_NUM*ROOM_NUM*MTN_REQUEST_NUM*RESIDENT_NUM)]
        db.session.add_all(mtn_task_data)
        db.session.commit()

        mtn_status_data = [new_mtn_status(faker, mtn_task.id) for mtn_task in mtn_task_data for _ in range(MTN_STATUS_NUM)]
        db.session.add_all(mtn_status_data)
        db.session.commit()

    click.echo("Data insertion completed.")