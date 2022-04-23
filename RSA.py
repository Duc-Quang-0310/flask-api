import random
import string


#STEP 1: Choose two prime numbers (p, q), such as p is not equal t

# TODO implement prime number generator
# For now, we assign two primes to p and q
#p = 11
#q = 29

def primes_in_range(x, y):
    prime_list = []
    for n in range(x, y):
        isPrime = True

        for num in range(2, n):
            if n % num == 0:
                isPrime = False
                
        if isPrime:
            prime_list.append(n)
    return prime_list

def get_ramdom_prime(x, y):
    list = primes_in_range(x, y)
    p = random.choice(list)
    list.remove(p)
    q = random.choice(list)
    return p,q 


#STEP 2: Find n – the product of these numbers. 
# This number n becomes modulus in both keys.

#n = p * q 


#STEP 3: Calculate ϕ(n) function (Euler’s totient), that is, 
# how many coprime with n are in range (1, n). 
# To put it simply, how many numbers in that range do not 
# share common factors with n. The formula for this is

def phi_of_n(p , q):
    return (p - 1) * (q - 1)



#STEP 4: Choose encryption key e, such that:
# 1 < e < ϕ(n)
# e must be coprime with N and ϕ(n). 
# In other words, the greatest common divisor for (e, n) 
# and for (e, ϕ(n)) should be 1.


def get_gcd(x, y):
    while(y):
        x, y = y, x % y
    return x


def get_encryption_key(n, phi_of_n):
    lst = [i for i in range(1, n+1)]
    e_list = []
    for i in lst:
        if (1 < i) and (i < phi_of_n):
            gcd = get_gcd(i, n)
            gcd_phi = get_gcd(i, phi_of_n)
            if (gcd == 1) and (gcd_phi == 1):
                e_list.append(i)
    if len(e_list) == 1:
        return e_list[0]
    else:
        return e_list[random.randint(1, len(e_list)-1)]   


#STEP 5: Choose decryption key d, such that d*e(mod ϕ(n)) = 1. 
# In the example below, we expand the range for d by 
# multiplying e by 25 (this is an arbitrary number).

def get_decryption_key(e, phi_of_n):
    d_list = []
    for i in range(e * 255):
        if (e * i) % phi_of_n == 1:
            d_list.append(i)
    return d_list[random.randint(1, len(d_list) - 1)]


#STEP 6: Generate public key and private key
def generate_keys():
    print("---------------------------------")
    p,q = get_ramdom_prime(19, 71)
    print("P =", p)
    print("Q =", q)
    n = p * q  
    print("N =", n)
    phi_func = phi_of_n(p, q)  
    print("Phi_func =", phi_func)
    print("---------------------------------")
    e = get_encryption_key(n, phi_func)
    d = get_decryption_key(e, phi_func)
    # to avoid key collision
    while d == e:
        d = get_decryption_key(e, phi_func)

    public_key = [e, n]  # [137, 319]
    private_key = [d, n]  # [1633, 319]

    return public_key, private_key



#Encryption

def text_to_digits(PT):
    pool = string.ascii_letters + string.punctuation + " "
    M = []
    for i in PT:
        M.append(pool.index(i))
    return M

def encrypt(M, public_key):
    return [(i ** public_key[0]) % public_key[1] for i in M]


#Decryption

def decrypt(CT, private_key):
    return [((i ** private_key[0]) % private_key[1]) for i in CT]

def digits_to_text(DT):
    pool = string.ascii_letters + string.punctuation + " "
    msg = ''
    for i in DT:
        msg += pool[i]
    return msg


#SIMPLIFY
#USE THESE 

def encode(message , public_key):
    M = text_to_digits(message)
    encoded_message = encrypt(M, public_key)
    return encoded_message

def decode(message, private_key):
    decoded_message = decrypt(message, private_key)
    return digits_to_text(decoded_message)


#MAIN
# print("*********************WELCOME****************************")

# message = input("What would you like encrypted :")
# print("Your message is :",message)

# public_key, private_key = generate_keys()
# print("Public key:", public_key)
# print("Private key:", private_key)
# print("------------------------------")

# encoded_msg = encode(message, public_key)
# print("This message is encoded:", encoded_msg)

# decoded_msg = decode(encoded_msg, private_key)
# print("-")
# print ("This message is decoded:",decoded_msg)

# print("-")
# if(message == decoded_msg) :
#     print("Success")
# else: 
#     print("Fail")

# print("********************GOODBYE*****************************")


