import rq
import redis

from app import db, app
from uuid import uuid4
from datetime import timedelta



class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    is_completed = db.Column(db.Boolean, default=False)

    api_user_key = db.Column(db.Integer, db.ForeignKey('api_user.api_user_key'))

    def __repr__(self):
        return f'<Job obj #{self.id}: API User Key: {self.api_user_key}>'

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @staticmethod
    def create(id, key):
        j = Job(id=id, api_user_key=api_key)
        db.session.add(j)
        db.session.commit()


class APIUser(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    api_calls = db.Column(db.Integer, default=0, nullable=False) 
    api_calls_limit = db.Column(db.Integer, default=5, nullable=False)
    api_call_interval = db.Column(db.Interval, nullable=False, default=timedelta(hours=12))
    
    api_user_key = db.Column(db.String(200), db.ForeignKey('api_key.key'), nullable=False)

    def __repr__(self):
        return f'<APIUser obj #{self.id}: Key: {self.api_user_key}, API Calls: {self.api_calls}/{self.api_calls_limit} per {self.api_call_interval}>'

    def flush_api_calls(self):
        self.api_calls = 0
        db.session.commit()
        return True

    @staticmethod
    def increment_api_calls_by_n(self, n=1):
        self.api_calls += n
        db.session.commit()
        return True

    @staticmethod
    def create(api_key):
        try:
            user = APIUser(api_user_key=api_key)
            db.session.add(user)
            db.session.commit()
        except:
            pass


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200), unique=True, nullable=False, default=lambda: uuid4().hex)
    is_valid = db.Column(db.Boolean, default=True)
    
    user = db.relationship('APIUser', backref='key_obj', uselist=False, lazy=True)

    def __repr__(self):
        return f'<APIKey obj #{self.id}: Key: {self.key}, Valid: {self.is_valid}>'


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





