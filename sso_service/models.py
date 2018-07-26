from datetime import datetime

from sso_service import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verified = db.Column(db.SmallInteger, default=1, nullable=False)
    mobile = db.Column(db.String(11), nullable=True)
    avatar = db.Column(db.String(100), nullable=False, default='')
    is_admin = db.Column(db.SmallInteger, nullable=False, default=0)
    company_id = db.Column(db.Integer)
    fake_email = db.Column(db.SmallInteger, nullable=False, default=0)


class WxUser(db.Model):
    __tablename__ = 'wx_user'

    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False,
        primary_key=True
    )
    auth_cancelled = db.Column(
        db.SmallInteger,
        nullable=False,
        default=0,
        server_default='0'
    )

    # Relationships
    user = db.relationship(
        'User',
        uselist=False,
        backref=db.backref(
            'wx_user',
            cascade="all, delete-orphan",
            single_parent=True,
            uselist=False
        )
    )


class WxCorp(db.Model):
    __tablename__ = 'wx_corp'

    id = db.Column(db.String(100), primary_key=True)
    perm_code = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer)
    auth_cancelled = db.Column(
        db.SmallInteger,
        nullable=False,
        default=0,
        server_default='0'
    )
    agent_id = db.Column(db.String(100), nullable=False, server_default='0')
    new_installation = db.Column(db.SmallInteger, nullable=False, default=1)
    status = db.Column(db.SmallInteger, nullable=False, default=0,
                       server_default='1')
