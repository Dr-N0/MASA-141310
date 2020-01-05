# MASA-141310

[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-360/)

Web API for interfacing with logging database, managing users, and permissions. Named after the Lockheed WV-2 Super Constellation, which was an airborne radar patrol flight that disappeared on February 20, 1958.

## Models

### Users

A user object represents a human. 

```
table_name = users

{
    "id": "0de8a5fc-b64f-4400-8902-5013e0691bd1",
    "email": "harmonherring@gmail.com",
    "username": "harmon",
    "password": "$argon2id$v=19$m=102400,t=2,p=8$Rja9ERxWEkAEZJ6OT8IltA$8CYRkDW/G57f9lfIq9HM+g",
    "is_owner": 't',
    "active": 't'
}
```

#### Endpoints

```
GET     /users/
POST    /users/
GET     /users/username/<username>/
DELETE  /users/username/<username>/
GET     /users/username/<username>/roles/
POST    /users/username/<username>/roles/
POST    /users/username/<username>/roles/<role_id>
```

### Role Definitions

Contains role name, id, and permissions. Roles can be assigned to users to allow partial API access.

```
table_name = role_descriptions

{
    "name": "Administrator",
    "id": 1,
    "get_log": 't',
    "post_log": 'f',
    "create_user": 't'
}
```

#### Endpoints

```
GET     /roles/
POST    /roles/
GET     /roles/name/<name>/
DELETE  /roles/name/<name>/
```

### Roles

Roles relate a user to a role definition.

```
table_name = roles

{
    "id": 1,
    "user_id": "0de8a5fc-b64f-4400-8902-5013e0691bd1",
    "role_id": 2
}
```

#### Endpoints

```
GET     /users/username/<username>/roles/
POST    /users/username/<username>/roles/
```

### Control Module Meta

Contains metadata for the control module on a plane.

```
table_name = cm_meta

{
    "id": "75a5874b-8a54-42b1-8c6b-a0f6945ccf2a",
    "name": "test
}
```

#### Endpoints

```
GET     /cm/
POST    /cm/
GET     /cm/name/<cm_name>/
DELETE  /cm/name/<cm_name>/
GET     /cm/id/<cm_uuid>/
DELETE  /cm/id/<cm_uuid>/
```

### Log Types

Contains the types of logs sent by a control module. Only used for quick searching, and is not a constraint of the log table.

```
table_name = cm_log_types

{
    "id": 7,
    "cm_uuid": "75a5874b-8a54-42b1-8c6b-a0f6945ccf2a",
    "log_type": "test",
    "description": "Used for testing.""
}
```

#### Endpoints

Subject to Change

```
GET     /log_types/<cm_uuid>
POST    /log_types/<cm_uuid>
DELETE  /log_types/<cm_uuid>/<log_type_name>
```

### Logs

Represents a log, associated to a Control Module and Log Type.

```
{
    "id": 9,
    "cm_uuid": "75a5874b-8a54-42b1-8c6b-a0f6945ccf2a",
    "log_type": "test",
    "data": 
        {
            "test": "data"
        }
    "timestamp": 2019-12-10 06:32:20.00954
}
```

#### Endpoints

```
GET     /logs/<cm_uuid>
POST    /logs/<cm_uuid>
```
