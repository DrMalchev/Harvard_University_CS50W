# Define a list of data
names = ["Harry", "Ron", "Hermione", "Ginny"]

def printList (list):
    for x in range(len(list)):
        print(list[x])


names.append("Draco")
names.sort()

print("List after new name addition and sorting")
printList(names)