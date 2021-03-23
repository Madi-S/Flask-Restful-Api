import rq
import redis

from uuid import uuid4
from datetime import timedelta
from app import db, app, logger, bcrypt



class FlushAPICallsJob(db.Model):
    job_id = db.Column(db.String(36), primary_key=True)
    api_user_key = db.Column(db.Integer, db.ForeignKey('api_user.api_user_key'))

    def __repr__(self):
        return f'<FlushAPICallsTask obj #{self.job_id}: API User Key: {self.api_user_key}>'

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @classmethod
    def create(cls, id, api_key):
        j = cls(job_id=id, api_user_key=api_key)
        db.session.add(j)
        db.session.commit()


class APIUser(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    api_calls = db.Column(db.Integer, default=0, nullable=False) 
    api_calls_limit = db.Column(db.Integer, default=5, nullable=False)
    api_call_interval = db.Column(db.Interval, nullable=False, default=timedelta(seconds=10))
    
    api_user_key = db.Column(db.String(200), db.ForeignKey('api_key.key'), nullable=False)

    password = db.Column(db.LargeBinary, nullable=False)
    username = db.Column(db.String(200), unique=True, nullable=False)

    def __repr__(self):
        return f'<APIUser obj #{self.id}: Key: {self.api_user_key}, API Calls: {self.api_calls}/{self.api_calls_limit} per {self.api_call_interval.seconds} seconds>'

    @staticmethod
    def validate_creds(username, password):
        user = APIUser.query.filter_by(username=username).first()

        if user:
            password_match = bcrypt.check_password_hash(user.password, str(password))
            if password_match:
                return True, 'Successful Login'

            return False, 'Passwords do not match!'
        return False, f'User {username} does not exist!'

    @staticmethod
    def create(username, password):
        if not APIUser.query.filter_by(username=username).first():
            pwd_hash = bcrypt.generate_password_hash(str(password))
            api_key = APIKey.create().key

            user = APIUser(
                username=username,
                password=pwd_hash,
                api_user_key=api_key
            )

            db.session.add(user)
            db.session.commit()
            return user

    def refresh_api_key(self):
        if self:
            api_key_obj = self.key_obj
            api_key_obj.is_valid = False

            new_api_key = APIKey.create().key
            self.api_user_key = new_api_key

            db.session.commit()
            return True, new_api_key

        return None, None


    def change_api_calls_by_n(self, n=1):
        if self:
            logger.debug('IN increment_api_calls_by_n')
            logger.debug('BEFORE: API_USER %s', self)

            self.api_calls += n
            db.session.commit()

            logger.debug('AFTER: API_USER %s', self)
            return True

    def flush_api_calls(self, key):
        '''
        Done in such terrible manner because rq worker raises ImportError, when working with staticmethod
        '''
        user = APIUser.query.filter_by(api_user_key=key).first()
        if user:
            logger.debug('IN flush_api_calls')
            logger.debug('BEFORE: API_USER %s', user)

            user.api_calls = 0
            db.session.commit()

            logger.debug('AFTER: API_USER %s', user)
            return True


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200), unique=True, nullable=False, default=lambda: uuid4().hex)
    is_valid = db.Column(db.Boolean, default=True)
    
    user = db.relationship('APIUser', backref='key_obj', uselist=False, lazy=True)

    def __repr__(self):
        return f'<APIKey obj #{self.id}: Key: {self.key}, Valid: {self.is_valid}>'

    @staticmethod
    def create():
        key = APIKey()
        
        db.session.add(key)
        db.session.commit()
        return key


class FakeUser(db.Model):
    middle_name = db.Column(db.String(100))
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey('fake_location.id'), nullable=False)

    def __repr__(self):
        return f'<FakeUser obj #{self.id}: {self.first_name} {self.last_name} {self.last_name}>'

    def jsonified(self):
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


class FakeLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(200), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(200), nullable=False)

    citizens = db.relationship('FakeUser', backref='location', lazy=True)

    def __repr__(self):
        return f'<FakeLocation object #{self.id}: country: {self.country}, city: {self.city}>'

    def jsonified(self):
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





