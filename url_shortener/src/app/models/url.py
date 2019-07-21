from flask import current_app
from app import db
import peewee

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Url(BaseModel):
    id = peewee.PrimaryKeyField()
    long_url = peewee.CharField()
    short_url = peewee.CharField()
   
    class Meta:
        db_table = 'urls'