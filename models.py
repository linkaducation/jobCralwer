from peewee import *

host = '127.0.0.1'
user = 'root'
password = '123456'
port = 3306

db = MySQLDatabase('job_crawler', **{'host': host, 'user': user, 'password': password, 'port': port})
db.connect()


class BaseModel(Model):
    class Meta:
        database = db


class Company(BaseModel):
    id = IntegerField(null=False)
    name = CharField(null=False)
    scale = CharField(null=True)
    nature = CharField(null=False)
    category = CharField(null=True)
    position = CharField(null=True)
    description = TextField(null=True)


class Job(BaseModel):
    id = IntegerField(null=False)
    company = ForeignKeyField(Company)
    name = CharField(null=False)
    city = CharField(null=False)
    minSalary = IntegerField(null=True)
    maxSalary = IntegerField(null=True)
    workYear = IntegerField(null=True)
    education = CharField(null=True)
    headCount = IntegerField(null=True)
    publishDate = DateTimeField(null=True)
    major = CharField(null=True)
    tag = TextField(null=True)
    description = TextField(null=True)
    function = CharField(null=True)
    position = CharField(null=True)
    uniqueId = CharField(null=False)
    jobUrl = CharField(null=False)


class Task(BaseModel):
    id = IntegerField(null=False)
    site = CharField(null=False)
    jobName = CharField(null=False)
    city = CharField(null=True)
    minSalary = IntegerField(null=True)
    maxSalary = IntegerField(null=True)
    companyNature = IntegerField(null=True)
    companyScale = CharField(null=True)
    education = CharField(null=True)
    workYear = IntegerField(null=True)
    addedDate = DateTimeField(null=False)
    finishedDate = DateTimeField(null=True)
    finished = BooleanField(default=False)
    user = IntegerField(null=False)
