class Flight():
    def __init__(self, capacity):
        self.capacity = capacity
        self.passengers = []
    
    def add_passenger(self, name):
        
        if not self.free_seats():
    #alternative -> if self.free_seats() ==0:
            return False
        self.passengers.append(name)
        return True

    # function add_passengers will add passengers without checking if capacity is available
    # therefore add another function to check free seats
    def free_seats(self):
        return self.capacity - len(self.passengers)

flight = Flight(3)
people = ["Harry", "Ron", "Harmione", "Ginny"]
for person in people:
    success = flight.add_passenger(person)
    if success:
        print(f"Person {person} added successfully.")
    else:
        print(f"No available seat for person {person}.")

    