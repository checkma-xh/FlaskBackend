from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER

from app import db


class MtnStatus(db.Model):
    __tablename__ = "mtn_status"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    detail        = db.Column(db.String(128), nullable=False)
    img_url       = db.Column(db.String(128), nullable=False)
    mtn_task_id   = db.Column(INTEGER(unsigned=True), db.ForeignKey('mtn_task.id', ondelete='CASCADE'), nullable=False)
    update_time   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id'         : self.id,
            'detail'     : self.detail,
            'img_url'    : self.img_url,
            'mtn_task_id': self.mtn_task_id,
            'update_time': self.update_time,
        }