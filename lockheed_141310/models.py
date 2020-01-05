import uuid
from datetime import datetime

import pytz
from sqlalchemy.dialects.postgresql import JSONB, UUID, TEXT, TIMESTAMP, BOOLEAN
from sqlalchemy import ForeignKey

from lockheed_141310 import db


class CMMeta(db.Model):
    __tablename__ = 'cm_meta'
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True)
    name = db.Column(TEXT)

    def __init__(self, name: str):
        self.uuid = uuid.uuid4()
        self.name = name

    @classmethod
    def create(cls, name: str) -> dict:
        new_meta = cls(name)
        db.session.add(new_meta)
        db.session.commit()
        return new_meta.to_dict()

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "name": self.name,
        }


class CMLog(db.Model):
    __tablename__ = 'cm_log'
    __table_args__ = (
        db.ForeignKeyConstraint(('cm_uuid', 'log_type'), ('cm_log_types.cm_uuid', 'cm_log_types.log_type')),
    )
    id = db.Column(db.Integer, primary_key=True)
    cm_uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4())
    timestamp = db.Column(TIMESTAMP)
    log_type = db.Column(TEXT)
    data = db.Column(JSONB)

    def __init__(self, cm_uuid: UUID, log_type: str, data: dict):
        self.cm_uuid = cm_uuid
        self.log_type = log_type
        self.timestamp = str(datetime.now(pytz.utc))
        self.data = data

    @classmethod
    def create(cls, cm_uuid: UUID, log_type: str, data: dict) -> dict:
        new_log = cls(cm_uuid, log_type, data)
        db.session.add(new_log)
        db.session.commit()
        return new_log.to_dict()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cm_uuid": self.cm_uuid,
            "timestamp": str(self.timestamp),
            "log_type": self.log_type,
            "data": self.data
        }


class Users(db.Model):
    __tablename__ = 'users'
    username = db.Column(TEXT, unique=True)
    password = db.Column(TEXT)
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True)
    is_owner = db.Column(BOOLEAN)
    active = db.Column(BOOLEAN)
    email = db.Column(TEXT, unique=True)

    def __init__(self, username: str, password: str, email: str, active: bool):
        self.username = username
        self.password = password
        self.id = uuid.uuid4()
        self.is_owner = False
        self.active = active
        self.email = email

    @classmethod
    def create(cls, username: str, hashed_password: str, email: str, active: bool = False) -> dict:
        new_user = cls(username, hashed_password, email, active)
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict()

    # TODO: differentiate role name vs role id, and change in add role route
    def has_role_name(self, search_role: str) -> bool:
        """
        Determines if user is member of role, given role name
        """
        roles = {role.id: role.name for role in RoleDefinitions.query.all()}
        owned_role_ids = [role.role_id for role in Roles.query.filter_by(user_id=self.id).all()]
        for owned_role_id in owned_role_ids:
            if roles[owned_role_id] == search_role:
                return True
        return False

    def has_role_id(self, role_id: int) -> bool:
        """
        Determines if user is member of role, given role id
        """
        owned_role_ids = [role.role_id for role in Roles.query.filter_by(user_id=self.id).all()]
        print(owned_role_ids)
        for owned_role_id in owned_role_ids:
            if owned_role_id == role_id:
                print("Match!")
                return True
        return False

    def roles(self):
        roles_query = Roles.query.filter_by(user_id=self.id).all()
        roles = []
        for role in roles_query:
            role_definition = RoleDefinitions.query.filter_by(id=role.role_id).first()
            role_data = {
                "role_id": role_definition.id,
                "name": role_definition.name,
            }
            roles.append(role_data)
        return roles

    def to_dict(self):
        return {
            "username": self.username,
            "id": self.id,
            "is_owner": self.is_owner,
            "roles": self.roles(),
            "active": self.active
        }


class RoleDefinitions(db.Model):
    __tablename__ = 'role_definitions'
    name = db.Column(TEXT, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    get_log = db.Column(BOOLEAN)
    post_log = db.Column(BOOLEAN)
    create_user = db.Column(BOOLEAN)
    delete_user = db.Column(BOOLEAN)
    create_role = db.Column(BOOLEAN)
    delete_role = db.Column(BOOLEAN)

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.get_log = kwargs.get("get_log", False)
        self.post_log = kwargs.get("post_log", False)
        self.create_user = kwargs.get("create_user", False)
        self.delete_user = kwargs.get("delete_user", False)
        self.create_role = kwargs.get("create_role", False)
        self.delete_role = kwargs.get("delete_role", False)

    @classmethod
    def create(cls, name: str, **kwargs) -> dict:
        new_role = cls(name, **kwargs)
        db.session.add(new_role)
        db.session.commit()
        return new_role.to_dict()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "get_log": self.get_log,
            "post_log": self.post_log,
            "create_user": self.create_user,
            "delete_user": self.delete_user,
            "create_role": self.create_role,
            "delete_role": self.delete_role
        }

    def has_permission(self, permission: str) -> bool:
        """
        Determines if user has permission
        """
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
    def create(cls, user_id: UUID, role_id: int) -> dict:
        new_role = cls(user_id, role_id)
        db.session.add(new_role)
        db.session.commit()
        return new_role.to_dict()

    def get_name(self) -> str:
        return RoleDefinitions.query.filter_by(id=self.role_id).first().name

    def has_permission(self, permission: str) -> bool:
        """
        Determines if role has the specified permission
        """
        definition = RoleDefinitions.query.filter_by(self.role_id).first()
        if hasattr(definition, permission):
            return getattr(definition, permission)
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id
        }


class CMLogTypes(db.Model):
    __tablename__ = 'cm_log_types'
    __table_args__ = (
        db.UniqueConstraint('cm_uuid', 'log_type', name='log_type'),
    )
    id = db.Column(db.Integer, primary_key=True)
    cm_uuid = db.Column(UUID, ForeignKey("cm_meta.uuid"))
    log_type = db.Column(TEXT)
    description = db.Column(TEXT)

    def __init__(self, cm_uuid: str, log_type: str, description: str):
        self.cm_uuid = cm_uuid
        self.log_type = log_type
        self.description = description

    @classmethod
    def create(cls, cm_uuid: str, log_type: str, description: str = None) -> dict:
        new_cm_log_type = cls(cm_uuid, log_type, description)
        db.session.add(new_cm_log_type)
        db.session.commit()
        return new_cm_log_type.to_dict()

    def to_dict(self):
        return {
            "id": self.id,
            "cm_uuid": self.cm_uuid,
            "log_type": self.log_type,
            "description": self.description
        }
