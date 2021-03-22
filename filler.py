from models import *
from faker import Faker
from random import choice

f = Faker()



def fake_location():
    return FakeLocation(
        city=f.city(),
        country=f.country(),
        zipcode=f.zipcode(),
    )

def fake_user():
    return FakeUser(
        last_name=f.last_name(),
        first_name=f.first_name(),
        middle_name=f.last_name(),
        location_id=choice(locations).id,
)

def api_key():
    return APIKey(

    )

def fill(n, func):
    objs = []
    for i in range(1, n + 1):
        objs.append(func())
        print(f'Object #{i} created: {func.__name__}')

    db.session.add_all(objs)
    db.session.commit()

    print('Commited')
    return True

if __name__ == '__main__':
    fill(100, fake_location)
    locations = FakeLocation.query.all()
    fill(200, fake_user)

    fill(100, api_key)