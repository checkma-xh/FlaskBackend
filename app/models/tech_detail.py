from sqlalchemy import CheckConstraint
from sqlalchemy import between
from sqlalchemy.dialects.mysql import INTEGER

from app import db


class TechDetail(db.Model): 
    __tablename__  = "tech_detail"
    id             = db.Column(INTEGER(unsigned=True), primary_key=True)
    mtn_tech_id    = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    mtn_count      = db.Column(INTEGER(unsigned=True), nullable=False, default=0)
    score          = db.Column(db.Float, nullable=True)
    __table_args__ = (CheckConstraint("(score BETWEEN 1 AND 5) OR (score IS NULL)", name='check_tech_detail_score'),)

    def to_dict(self):
        return {
            'id'         : self.id,
            'mtn_tech_id': self.mtn_tech_id,
            'mtn_count'  : self.mtn_count,
            'score'      : self.score,
        }