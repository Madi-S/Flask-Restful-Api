import rq
import redis

from app import db, app
from uuid import uuid4
from datetime import timedelta



class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    is_completed = db.Column(db.Boolean, default=False)

    key = db.Column(db.Integer, db.ForeignKey('api_user.key'))

    def __repr__(self):
        return f'<Job obj #{self.id}: {self.name}, {self.description}>'

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @staticmethod
    def create(id, api_key):
        j = Job(id=id, key=api_key)
        db.session.add(j)
        db.session.commit()


class APIUser(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    api_calls = db.Column(db.Integer, default=0, nullable=False) 
    api_calls_limit = db.Column(db.Integer, default=5, nullable=False)
    api_call_interval = db.Column(db.Interval, nullable=False, default=timedelta(hours=12))
    
    key = db.Column(db.String, db.ForeignKey('api_key.key'), nullable=False)

    def __repr__(self):
        return f'<APIUser obj #{self.id}: {self.key}, {self.api_calls}>'

    # def launch_task(self, name, description, *args, **kwargs):
    #     rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
    #                                             *args, **kwargs)
    #     task = Task(id=rq_job.get_id(), name=name, description=description,
    #                 user=self)
    #     db.session.add(task)
    #     return task

    def flush_api_calls(self):
        self.api_calls = 0
        db.session.commit()
        return True

    @staticmethod
    def increment_api_calls_by_n(self, n=1):
        self.api_calls += n
        db.session.commit()
        return True


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Integer, unique=True, default=lambda: uuid4().hex)
    is_valid = db.Column(db.Boolean, default=True)
    
    user = db.relationship('APIUser', backref='key_obj', uselist=False, lazy=True)

    def __repr__(self):
        return f'<APIKey obj #{self.id}: {self.key}, {self.is_valid}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

    def __repr__(self):
        return f'<User obj #{self.id}: {self.first_name} {self.last_name} {self.last_name}>'

    def jsonified_obj(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'location': {
                'id': self.location_id,
                'country': self.location.country,
                'city': self.location.city,
                'zipcode': self.location.zipcode
            }
        }


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)

    citizens = db.relationship('User', backref='person', lazy=True)

    def __repr__(self):
        return f'<Location object #{self.id}: country: {self.country}, city: {self.city}>'

    def jsonified_obj(self):
        data =  {
            'id': self.id,
            'city': self.city,
            'country': self.country,
            'zipcode': self.zipcode,
            'citizens_count': len(self.citizens),
            'citizens': [],
        }
        for citizen in self.citizens:
            data['citizens'].append({
                citizen.jsonified_obj()
            })
        return data





