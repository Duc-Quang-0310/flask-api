import math

from numpy import append
import common.constants as constant


def get_string_length_and_order(length_and_order: str):
    length = 0
    order = ""

    if "na" in length_and_order:
        order = "na"
        length_and_order = length_and_order.replace("na", "")
    else:
        order = "re"
        length_and_order = length_and_order.replace("re", "")

    length = int(length_and_order)

    return [order, length]


def str_length_with_position(length: int, order_arr: list[int]):
    total_char: list[int] = []
    attempts = 2000
    length_tmp = length
    appearance = 0

    for index in range(math.ceil(length / 3)):
        total_char.append(0)

    while attempts > 0:
        for i in range(math.ceil(length / 3)):
            if order_arr[i] == appearance:
                if length_tmp > 3:
                    total_char[i] = 3
                else:
                    total_char[i] = length_tmp

                length_tmp = length_tmp - 3
                appearance += 1

        if 0 not in total_char:
            break

    return total_char


def get_actual_hash_phrase(encode_arr: list[str], order: constant.order, order_arr: list[int]):
    result: list[str] = []
    for each in encode_arr:
        for spice in constant.spice:
            match_char = 0
            for index in range(len(spice)):
                if spice[index] in each:
                    match_char += 1

            if (match_char == 6):
                break

        decode_phase = each[6:9]
        if (order == "re"):
            result.append(decode_phase[::-1])
        else:
            result.append(decode_phase)

    return re_align_decode(order_arr, result)


def re_align_decode(order_arr: list[int], raw_result: list[str]) -> str:
    for index in range(len(order_arr) - 1):
        temp = index + 1
        for next_index in range(len(order_arr) - temp):
            next_index = next_index + index + 1
            if order_arr[next_index] < order_arr[index]:
                tmp = order_arr[index]
                order_arr[index] = order_arr[next_index]
                order_arr[next_index] = tmp
                tmp = raw_result[index]
                raw_result[index] = raw_result[next_index]
                raw_result[next_index] = tmp
    return ''.join(raw_result)


def decoder(length: int, order: constant.order, shuffle_order: str, hash_password: str, current_password: str):
    match = True
    order_array: list[int] = []
    hash_array: list[str] = []

    for index in range(len(shuffle_order)):
        order_array.append(int(shuffle_order[index]))

    char_length_arr = str_length_with_position(length, order_array)

    for char_sequence in range(len(char_length_arr)):
        tmp_split_string = hash_password[0: 6 + char_length_arr[char_sequence]]
        hash_array.append(tmp_split_string)
        hash_password = hash_password.replace(tmp_split_string, "")

    store_password = get_actual_hash_phrase(hash_array, order, order_array)

    if (current_password != store_password):
        match = False
    return match


def decode_main(string_hash: str, current_password: str) -> str:

    split_array = string_hash.split("&")
    length_and_order = split_array[1]
    hash_password = split_array[2]
    shuffle_order = split_array[3]

    tmp = get_string_length_and_order(length_and_order)
    password_length = tmp[1]
    hash_order = tmp[0]

    final = decoder(password_length, hash_order, shuffle_order,
                    hash_password, current_password)

    return final
