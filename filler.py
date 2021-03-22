from models import *
from faker import Faker
from random import choice

f = Faker()


def fake_location(i):
    return FakeLocation(
        city=f.city(),
        country=f.country(),
        zipcode=f.zipcode(),
    )


def fake_user(i):
    return FakeUser(
        last_name=f.last_name(),
        first_name=f.first_name(),
        middle_name=f.last_name(),
        location_id=locations[i].id,
    )


def api_user(i):
    return APIUser(api_user_key=keys[i].key)


def api_key(i):
    return APIKey()


def fill(n, func):
    objs = []
    for i in range(n):
        objs.append(func(i))
        logger.debug('Object #%s created %s', i+1, func.__name__)

    db.session.add_all(objs)
    db.session.commit()

    logger.debug('Commited')
    return True


if __name__ == '__main__':
    db.drop_all()
    db.session.commit()
    logger.debug('DB TABLES DROPED')

    db.create_all()
    db.session.commit()
    logger.debug('DB TABLES CREATED')

    fill(100, fake_location)
    locations = FakeLocation.query.all()
    fill(100, fake_user)

    fill(100, api_key)
    keys = APIKey.query.all()
    fill(100, api_user)
