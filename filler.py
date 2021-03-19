from models import *
from faker import Faker
from random import choice

f = Faker()



def country():
    return Location(
        city=f.city(),
        country=f.country(),
        zipcode=f.zipcode(),
    )

def user():
    return User(
        last_name=f.last_name(),
        first_name=f.first_name(),
        middle_name=f.last_name(),
        location_id=choice(locations).id,
)

def fill(n, func):
    objs = []
    for i in range(n):
        objs.append(func())
        print(f'Object #{i} created')

    db.session.add_all(objs)
    db.session.commit()

    print('Commited')
    return True

if __name__ == '__main__':
    fill(100, country)
    locations = Location.query.all()
    fill(200, user)