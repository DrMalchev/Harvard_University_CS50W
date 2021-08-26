import sys

try:
    x = int(input("x= "))
    y = int(input("y= "))
except ValueError:
    print("Error: Value is not an integer")
    sys.exit(1)

try:
    result = x / y
except ZeroDivisionError:
    print("Error: Can not divide by zero")
    sys.exit(1)


print(f"{x} / {y} = {result}")