from sqlalchemy.dialects.mysql import INTEGER

from app import db


class Org(db.Model): 
    __tablename__ = "org"
    id            = db.Column(INTEGER(unsigned=True), primary_key=True)
    detail        = db.Column(db.String(128), nullable=False)
    name          = db.Column(db.String(18), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id'    : self.id,
            'detail': self.detail,
            'name'  : self.name,
        }