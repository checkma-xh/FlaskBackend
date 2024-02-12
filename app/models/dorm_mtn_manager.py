from sqlalchemy.dialects.mysql import INTEGER

from app import db


class DormMtnManager(db.Model): 
    __tablename__ = "dorm_mtn_manager"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    dorm_id       = db.Column(INTEGER(unsigned=True), db.ForeignKey('dorm.id', ondelete='CASCADE'), nullable=False)
    mtn_tech_id   = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    def to_dict(self):
        return {
            'id'         : self.id,
            'dorm_id'    : self.dorm_id,
            'mtn_tech_id': self.mtn_tech_id,
        }