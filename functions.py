import hashlib
import string
from datetime import datetime
from hashlib import md5

def div(a, b):
    return a / b


def analyze_pesel(pesel):
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    weight_index = 0
    digits_sum = 0

    for digit in pesel[:-1]:
        digits_sum += int(digit) * weights[weight_index]
        weight_index += 1

    pesel_modulo = digits_sum % 10
    validate = 10 - pesel_modulo

    if validate == 10:
        validate = 0

    gender = "male" if int(pesel[-2]) % 2 != 0 else "female"
    birth_date = datetime(
        int("19" + pesel[0:2]),
        int(pesel[2:4]),
        int(pesel[4:6]),
    )
    result = {
        "pesel": pesel,
        "valid": validate == int(pesel[-1]),
        "gender": gender,
        "birth_date": birth_date
    }
    return result

def calculate_vat(net_price, vat):
    return int((net_price * vat) / 100)

def hash_password(password):
    byte_password = password.encode()
    print(byte_password)
    if len(password) < 9:
        return None
    if all(not chr(c).islower() for c in byte_password):
        return None
    if all(not chr(c).isupper() for c in byte_password):
        return None
    if all(not chr(c).isdigit() for c in byte_password):
        return None
    if all(not chr(c) in string.punctuation for c in byte_password):
        return None
    return hashlib.md5(byte_password).hexdigest()
# encode konwertuje string na bytecode
