from sqlalchemy.dialects.mysql import INTEGER

from app import db


class Dorm(db.Model): 
    __tablename__ = "dorm"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    name          = db.Column(db.String(18), nullable=False)
    org_id        = db.Column(INTEGER(unsigned=True), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    mtn_count     = db.Column(INTEGER(unsigned=True), nullable=False, default=0)

    def to_dict(self):
        return {
            'id'           : self.id,
            'name'         : self.name,
            'org_id'       : self.org_id,
            'mtn_count'    : self.mtn_count,
        }