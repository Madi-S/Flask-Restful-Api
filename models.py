from app import db
from uuid import uuid4
from datetime import timedelta



class JobQueue:
    __tablename__ = 'job_queue'
    to_eval = db.Column(db.String(200))
    id = db.Column(db.Integer, primary_key=True)
    api_user_key = db.Column(db.Integer, db.ForeignKey('api_user.key'), nullable=False)


class APIKey(db.Model):
    __tablename__ = 'api_key'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Integer, unique=True, default=lambda: uuid4().hex)
    api_user = db.relationship('api_user', backref='person', uselist=False, lazy=True)
    is_valid = db.Column(db.Boolean, default=True)


class APIUser(db.Model):
    __tablename__ = 'api_user'
    id = db.Column(db.Integer, primary_key=True)
    api_calls = db.Column(db.Integer, default=0, nullable=False) 
    api_calls_limit = db.Column(db.Integer, defalut=5, nullable=False)
    key = db.Column(db.String, db.ForeignKey('api_key.key'), nullable=False)
    api_call_interval = db.Column(db.Interval, nullable=False, default=timedelta(hours=12))

    @staticmethod
    def flush_api_calls(api_user_key):
        api_user = APIUser.query.filter_by(key=api_user_key).first()
        if api_user:
            api_user.api_calls = 0
            db.session.commit()
            return True

    @staticmethod
    def increment_api_calls_by_n(api_user_key, n):
        api_user = APIUser.query.filter_by(key=api_user_key).first()
        if api_user:
            api_user.api_calls += 0
            db.session.commit()
            return True



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





