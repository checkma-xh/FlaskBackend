from sqlalchemy.dialects.mysql import INTEGER

from app import db


class Role(db.Model): 
    __tablename__ = "role"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    detail        = db.Column(db.String(128), nullable=False)
    name          = db.Column(db.String(18), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id'    : self.id,
            'detail': self.detail,
            'role'  : self.name,
        }