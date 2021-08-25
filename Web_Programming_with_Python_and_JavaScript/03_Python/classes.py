class Point():
    def __init__(self, input1, input2):
        # functions saves the inputs inside of the object
        self.x = input1
        self.y = input2

p = Point(2,8) 
# self argument is provided automatically
# but we must provide input1 and input2

print(p.x)
print(p.y)