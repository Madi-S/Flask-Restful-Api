import requests

BASE = 'http://127.0.0.1:5000/'

# r = requests.get(BASE + 'hello')
# print(r.json())

# r = requests.post(BASE + 'hello', data={'token': '54612315', 'age': 25})
# print(r.json())

# r = requests.get(BASE + 'health/62/73')
# print(r.json())


# r = requests.put(BASE + 'test/54', {'name': 'Madi', 'age': 17, 'gender': 'male'})
# print(r.json())

# r = requests.get(BASE + 'test/54')
# print(r.json())

# r = requests.delete(BASE + 'test/54')
# print(r.json())

# r = requests.get(BASE + 'test/54')
# print(r.json())


r = requests.get(BASE + '/faker/2b5f30c1e04840aaa8953ea2132f4feb')
print(r)