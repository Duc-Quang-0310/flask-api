from random import randint
import common.constants as constant
import math


def hash(un_hash_string: str, order: constant.order):
    hash_string: str = ""
    tmp: list[int] = [0, 1, 2, 3, 4, 5]
    random_spice: str = constant.spice[randint(0, len(constant.spice) - 1)]
    element_index = constant.shuffle_item_in_array(tmp)

    for index in element_index:
        hash_string = hash_string + str(random_spice[index])

    if order in constant.order_natural:
        return hash_string + un_hash_string
    return hash_string + un_hash_string[::-1]


def encode_main(password: str, order: constant.order) -> str:
    password_length: int = len(password)
    number_of_collection: float = password_length / 3
    hash_array: list[str] = []
    swap_index_array: list[int] = []
    hash_password: str = ''
    join: str = ""

    for index in range(math.ceil(number_of_collection)):
        print(index)
        start_index = index * 3
        end_index = start_index + 3
        splited_password = password[start_index: end_index]
        hash_array.append(hash(splited_password, order))
        swap_index_array.append(index)

    swap_index_array = constant.shuffle_item_in_array(swap_index_array)

    for index in swap_index_array:
        hash_password += hash_array[index]
        join += str(index)

    return f"&{password_length}{order}&{hash_password}&{join}"
