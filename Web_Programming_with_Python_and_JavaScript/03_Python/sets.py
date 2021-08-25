# Create an empty set
s = set()

# Add elements to the set
s.add(1)
s.add(2)
s.add(3)
s.add(4)
s.add(3) # 3 is already in the set, so it wont be added
print(s)

s.remove(2)
# Remove the value 2, not index 2
print(s)

print(f"The set contains {s.__len__()} elements")
print(f"The set contains {len(s)} elements")