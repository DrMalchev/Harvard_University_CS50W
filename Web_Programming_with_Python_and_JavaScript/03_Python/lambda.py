people = [
    {"name": "Harry", "house": "Gryffindor"},
    {"name": "Cho", "house": "Ravenclaw"},
    {"name": "Draco", "house": "Slytherin"}
]

""" def f(person):
    return person["name"]

people.sort(key=f) """

people.sort(key=lambda x: x["name"])
print(people)