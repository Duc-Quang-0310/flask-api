import os
import math
from random import randint
from typing import NewType

get = "GET"
post = "POST"
put = "PUT"
patch = "PATCH"
delete = "DELETE"
internal_server_error = "Internal Server Error"
normal_from = "apllication/json"
order = NewType('order', str)

port = str(os.environ.get("PORT")) or "5555"
db_prefix = 'mongodb+srv://'
db_username = str(os.environ.get("DATABASE_USERNAME"))
db_password = str(os.environ.get("DATABASE_PASSWORD"))
db_config = str(os.environ.get("DATABASE_CONFIG"))
db_connection = str(os.environ.get("DATABASE_CONNECTION"))

order_natural = "natural"
order_reverse = "reverse"

cloudinary_name = str(os.environ.get("CLOUD_NAME"))
cloudinary_api_key = str(os.environ.get("API_KEY"))
cloudinary_api_secret = str(os.environ.get("API_SECRET"))

spice = [
    "vbTcG7",
    "bWZ4IN",
    "SZky3n",
    "zccMcN",
    "hj1g1G",
    "ZXaTj8",
    "RgOKlO",
    "npjYXt",
    "t6sl1U",
    "fnqpFb",
    "lQeFMJ",
    "CiNAMO",
    "mHmLcz",
    "C6y2TM",
    "LYO7WS",
    "ZtHNOO",
    "ApmkhH",
    "QXJ0XV",
    "9MbUjl",
    "OjxV0K",
    "EljuNr",
    "Y3g2SI",
    "CMb97j",
    "GirbqW",
    "3xkPT3",
    "oiOBjg",
    "G4JVqQ",
    "7i9JPu",
    "cODKhM",
    "l59aKF",
]


def connection_string() -> str:
    return db_prefix + db_username + ':' + db_password + db_config


def shuffle_item_in_array(init: list[any]) -> list[any]:
    init_length: int = len(init)
    position: list[int] = []
    result: list[any] = []
    random_position: int = randint(0, init_length - 1)

    while len(position) != init_length:
        while(random_position in position):
            random_position = randint(0, init_length - 1)
        position.append(random_position)

    for index in position:
        result.append(init[index])

    return result


def get_port() -> int:
    return 5555
