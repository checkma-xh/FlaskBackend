from sqlalchemy.dialects.mysql import INTEGER

from app import db


class Room(db.Model): 
    __tablename__ = "room"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    dorm_id       = db.Column(INTEGER(unsigned=True), db.ForeignKey('dorm.id', ondelete='CASCADE'), nullable=False)
    mtn_count     = db.Column(INTEGER(unsigned=True), nullable=False, default=0)
    room_num      = db.Column(INTEGER(unsigned=True), nullable=False)

    def to_dict(self):
        return {
            'id'      : self.id,
            'dorm_id' : self.dorm_id,
            'room_num': self.room_num,
        }