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


def fill_fake(n, func):
    objs = []
    for i in range(n):
        objs.append(func(i))
        logger.debug('Object #%s created %s', i+1, func.__name__)

    db.session.add_all(objs)
    db.session.commit()

    logger.debug('Commited')
    return True

# --- REAL OBJECTS ---


def fill_api_user(n):
    for i in range(n):
        password = '12345'  # f.password()
        username = f.unique.user_name()
        APIUser.create(username, password)
        logger.debug('API User #%s created %s:%s', i+1, password, username)
    logger.debug('%s API Users created', n)


if __name__ == '__main__':
    db.drop_all()
    db.session.commit()
    logger.debug('DB TABLES DROPED')

    db.create_all()
    db.session.commit()
    logger.debug('DB TABLES CREATED')

    fill_fake(100, fake_location)

    locations = FakeLocation.query.all()
    fill_fake(100, fake_user)

    fill_api_user(10)
