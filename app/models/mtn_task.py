from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db


class MtnTask(db.Model):
    __tablename__  = "mtn_task"
    id             = db.Column(INTEGER(unsigned=True), primary_key=True)
    dorm_admin_id  = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    mtn_request_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('mtn_request.id', ondelete='CASCADE'), nullable=False)
    mtn_tech_id    = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    proc_time      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id'            : self.id,
            "dorm_admin_id" : self.dorm_admin_id,
            'mtn_request_id': self.mtn_request_id,
            'mtn_tech_id'   : self.mtn_tech_id,
            'proc_time'     : self.proc_time,
        }