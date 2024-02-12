from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy.dialects.mysql import INTEGER

from app import db


class User(db.Model):
    __tablename__    = "user"
    id               = db.Column(INTEGER(unsigned=True), primary_key=True)
    account          = db.Column(INTEGER(unsigned=True), nullable=False, unique=True)
    name             = db.Column(db.String(18), nullable=False)
    org_id           = db.Column(INTEGER(unsigned=True), db.ForeignKey("org.id", ondelete='CASCADE'), nullable=False)
    pwd_hash         = db.Column(db.String(256), nullable=False)
    phone            = db.Column(db.String(18), nullable=False)
    role_id          = db.Column(INTEGER(unsigned=True), db.ForeignKey("role.id", ondelete='CASCADE'), nullable=False)

    def set_pwd(self, pwd):
        self.pwd_hash = generate_password_hash(pwd)

    def validate_pwd(self, pwd):
        return check_password_hash(self.pwd_hash, pwd)

    def to_dict(self):
        return {
            "id"     : self.id,
            "account": self.account,
            "name"   : self.name,
            "org_id" : self.org_id,
            "phone"  : self.phone,
            "role_id": self.role_id,
        }