import rq
from uuid import uuid4
from datetime import timedelta, datetime
from app import db, app, logger, bcrypt



class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(230), nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    # date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Message obj #{self.id}: Text: {self.text}, Sender: {self.sender}, Category: {self.category}>'

    @staticmethod
    def create(text, sender, category):
        msg =  Message(
            text=text,
            sender=sender,
            category=category,
        )
        db.session.add(msg)
        db.session.commit()
        return msg

    @staticmethod
    def get_last_n_msgs(n=50):
        return Message.query.order_by(Message.id.desc()).limit(n).all()[::-1]

    @staticmethod
    def get_msgs_containing(text, n=100):
        search = f'%{text}%'
        return Message.query.filter(Message.text.like(search)).limit(n).all()


class APIUser(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    api_calls = db.Column(db.Integer, default=0, nullable=False) 
    api_calls_limit = db.Column(db.Integer, default=100, nullable=False)
    api_call_interval = db.Column(db.Interval, nullable=False, default=timedelta(hours=24))
    
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

    def jsonified(self):
        return {
            
        }

    def refresh_api_key(self):
        if self:
            api_key_obj = self.key_obj
            api_key_obj.is_valid = False

            new_api_key = APIKey.create().key
            self.api_user_key = new_api_key

            db.session.commit()
            return True, new_api_key

        return False, None


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


class CreateFakeMixin():

    @classmethod
    def create(cls, **kwargs):
        try:
            obj = cls(**kwargs)
            db.session.add(obj)
            db.session.commit()
            return obj
        except:
            logger.exception('Failed to create FakeMixn for %s with %s', cls.__name__, kwargs)


class FakeUser(CreateFakeMixin, db.Model):
    middle_name = db.Column(db.String(100))
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey('fake_location.id'), nullable=False)

    fields = ('middle_name', 'first_name', 'last_name', 'location_id')

    def __repr__(self):
        return f'<FakeUser obj #{self.id}: {self.first_name} {self.last_name} {self.middle_name}>'

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

    @staticmethod
    def update(id, **fields):
        fake_user = FakeUser.query.get(id)
        if fake_user:
            for column, value in fields.items():
                if not column in FakeUser.fields:
                    return False, None
                if value:
                    setattr(fake_user, column, value)
    
        db.session.commit()
        return True, fake_user


class FakeLocation(CreateFakeMixin, db.Model):
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





