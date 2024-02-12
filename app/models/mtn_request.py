from datetime import datetime
from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.mysql import INTEGER

from app import db


class MtnRequest(db.Model):
    __tablename__  = "mtn_request"
    id             = db.Column(INTEGER(unsigned=True), primary_key=True)
    completed      = db.Column(db.Boolean, nullable=False, default=False)
    detail         = db.Column(db.String(128), nullable=False)
    feedback       = db.Column(db.String(128), nullable=True)
    img_url        = db.Column(db.String(128), nullable=False)
    resident_id    = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    request_time   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    score          = db.Column(INTEGER(unsigned=True), nullable=True)
    ert            = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (CheckConstraint("(score BETWEEN 1 AND 5) OR (score IS NULL)", name='check_mtn_request_score'),)

    def to_dict(self):
        return {
            'id'          : self.id,
            'completed'   : self.completed,
            'detail'      : self.detail,
            'feedback'    : self.feedback,
            'img_url'     : self.img_url,
            'resident_id' : self.resident_id,
            'request_time': self.request_time,
            'score'       : self.score,
            'ert'         : self.ert,
        }