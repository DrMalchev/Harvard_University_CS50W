from prime import is_prime

def test_prime(n, expected):
    #expected is true or false
    if is_prime(n)!= expected:
        print("Error")