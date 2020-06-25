import flask

import json
from models.db import db
import datetime
from bson.objectid import ObjectId
from mongoengine import ValidationError

class MainModel(db.Document):
    meta = {
        'abstract': True
    }
    create_date = db.DateTimeField(default = datetime.datetime.now())
    modify_date = db.DateTimeField(default = datetime.datetime.now())
