from sqlalchemy.dialects.mysql import INTEGER

from app import db


class ResInfo(db.Model): 
    __tablename__ = "res_info"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    room_id       = db.Column(INTEGER(unsigned=True), db.ForeignKey('room.id', ondelete='CASCADE'), nullable=False)
    resident_id   = db.Column(INTEGER(unsigned=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id'         : self.id,
            'room_id'    : self.room_id,
            'resident_id': self.resident_id,
        }