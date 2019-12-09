import uuid
from datetime import datetime

import pytz
from sqlalchemy.dialects.postgresql import JSONB, UUID, TEXT, TIMESTAMP, BOOLEAN
from sqlalchemy import ForeignKey

from lockheed_141310 import db, ph


class CMMeta(db.Model):
    __tablename__ = 'cm_meta'
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True)
    name = db.Column(TEXT)

    def __init__(self, name: str):
        self.uuid = uuid.uuid4()
        self.name = name

    @classmethod
    def create(cls, name: str):
        new_meta = cls(name)
        db.session.add(new_meta)
        db.session.commit()


class CMLog(db.Model):
    __tablename__ = 'cm_log'
    id = db.Column(db.Integer, primary_key=True)
    cm_uuid = db.Column(UUID(as_uuid=True), ForeignKey('cm_meta.uuid'), default=uuid.uuid4())
    timestamp = db.Column(TIMESTAMP)
    log_type = db.Column(TEXT)
    data = db.Column(JSONB)

    def __init__(self, cm_uuid: UUID, log_type: str, data: dict):
        self.cm_uuid = cm_uuid
        self.log_type = log_type
        self.timestamp = str(datetime.now(pytz.utc))
        self.data = data

    @classmethod
    def create(cls, cm_uuid: UUID, log_type: str, data: dict):
        new_log = cls(cm_uuid, log_type, data)
        db.session.add(new_log)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "timestamp": str(self.timestamp),
            "log_type": self.log_type,
            "data": self.data
        }


class Users(db.Model):
    __tablename__ = 'users'
    username = db.Column(TEXT)
    password = db.Column(TEXT)
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True)
    is_owner = db.Column(BOOLEAN)

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = ph.hash(password)
        self.id = uuid.uuid4()
        self.is_owner = False

    @classmethod
    def create(cls, username: str, password: str):
        new_user = cls(username, password)
        db.session.add(new_user)
        db.session.commit()

    # TODO: differentiate role name vs role id, and change in add role route
    def has_role_name(self, search_role: str):
        roles = {role.id: role.name for role in RoleDefinitions.query.all()}
        owned_role_ids = [role.role_id for role in Roles.query.filter_by(user_id=self.id).all()]
        for owned_role_id in owned_role_ids:
            if roles[owned_role_id] == search_role:
                return True
        return False

    def has_role_id(self, role_id: int) -> bool:
        """
        Takes a role id as input and returns a boolean describing whether or not this user is a member of that role
        """
        owned_role_ids = [role.role_id for role in Roles.query.filter_by(user_id=self.id).all()]
        for owned_role_id in owned_role_ids:
            if owned_role_id == role_id:
                return True
        return False


class RoleDefinitions(db.Model):
    __tablename__ = 'role_descriptions'
    name = db.Column(TEXT)
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(BOOLEAN)
    get_log = db.Column(BOOLEAN)
    post_log = db.Column(BOOLEAN)

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.is_admin = kwargs.get("is_admin", False)
        self.get_log = kwargs.get("get_log", False)
        self.post_log = kwargs.get("post_log", False)

    @classmethod
    def create(cls, name: str, **kwargs):
        new_role = cls(name, kwargs=kwargs)
        db.session.add(new_role)
        db.session.commit()

    def to_json(self):
        return {
            "name": self.name,
            "is_admin": self.is_admin,
            "get_log": self.get_log,
            "post_log": self.post_log
        }

    def has_permission(self, permission: str):
        if hasattr(self, permission):
            return getattr(self, permission)
        return False


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey('users.id'), default=uuid.uuid4())
    role_id = db.Column(db.Integer, ForeignKey('role_descriptions.id'))

    def __init__(self, user_id: UUID, role_id: int):
        self.user_id = user_id
        self.role_id = role_id

    @classmethod
    def create(cls, user_id: UUID, role_id: int):
        new_role = cls(user_id, role_id)
        db.session.add(new_role)
        db.session.commit()

    def get_name(self):
        return RoleDefinitions.query.filter_by(id=self.role_id).first().name

    def has_permission(self, permission: str):
        definition = RoleDefinitions.query.filter_by(self.role_id).first()
        if hasattr(definition, permission):
            return getattr(definition, permission)
        return False
