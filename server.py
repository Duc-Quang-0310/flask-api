from flask import Flask, Response, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS

import common.constants as constants
import common.hash as algorithm
import common.decode as solver
import json

app = Flask(__name__)
CORS(app)

try:
    mongo = MongoClient(
        "mongodb+srv://ducquang0310:OpmJlSTokUUDFUaz@cluster0.s0rnm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    database = mongo.test
    db = mongo.company
    mongo.server_info()  # trigger when it cannot connect to mongo

except BaseException as error:
    print("ERROR - Cannot connect to mongo", error)
    raise

#######################################################################


@app.route("/users", methods=[constants.post])
def create_user():
    try:

        user = {
            "name": request.form['name'],
            "lastName": request.form['lastName']
        }

        db_response = db.users.insert_one(user)
        db_response.inserted_id

        return Response(
            response=json.dumps({
                "message": "user created",
                "id": f"{db_response.inserted_id}"
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )

    except error:
        print('Error at create_user(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )

#######################################################################


@app.route("/users", methods=[constants.get])
def get_some_user():
    try:
        data = list(db.users.find())

        for user in data:
            user["_id"] = str(user["_id"])

        tmp = "&11na&OKgOlRng1qWGribQuaHhkAmpDucaKl5F923&2103"
        solver.decode_main(tmp, "DucQuang12")

        return Response(
            response=json.dumps(data),
            status=200,
            mimetype=f"{constants.normal_from}",
        )
    except error:
        print('Error at get_some_user(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )

#######################################################################


@app.route("/users/<id>", methods=[constants.patch])
def update_user(id):
    try:
        db_response = db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": request.form["name"]}}
        )

        for attr in dir(db_response):
            print(f"{attr}")

        return Response(
            response=json.dumps({
                "message": "Updated"
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )
    except error:
        print('Error at update_user(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )

#######################################################################


@app.route("/users/<id>", methods=[constants.delete])
def delete_user(id):
    try:
        db_response = db.users.delete_one({"_id": ObjectId(id)})

        for attr in dir(db_response):
            print(f"{attr}")

        return Response(
            response=json.dumps({
                "message": "User Deleted"
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )
    except error:
        print('Error at update_user(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )

#######################################################################


@app.route("/account/sign-in", methods=[constants.post])
def logging():
    try:
        # request.get_json = equal to req.body in nodejs
        body = request.get_json()
        username = body['username']
        password = body['password']

        record = db.account.find_one({"username": username})
        if record == None:
            return Response(
                response=json.dumps({
                    "reason": "This email haven't existed in our database, register instead"
                }),
                status=400,
                mimetype=f"{constants.normal_from}",
            )

        check_match = solver.decode_main(record['password'], password)

        if check_match == False:
            return Response(
                response=json.dumps({
                    "reason": "Username or password is incorrect, please re-enter"
                }),
                status=400,
                mimetype=f"{constants.normal_from}",
            )

        user_id = record['_id']

        return Response(
            response=json.dumps({
                "message": "Sign in successfully",
                "userId": f"{user_id}"
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )
    except error:
        print('Error at logging(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )

#######################################################################


@app.route("/account/sign-up", methods=[constants.post])
def new_account():
    try:
        # request.get_json = equal to req.body in nodejs
        body = request.get_json()
        username = body['username']
        password = body['password']
        error_occur = False

        record = list(db.account.find({"username": username}))

        for account in record:
            temp = str(account["username"])

            if temp == username:
                error_occur = True

            if error_occur == True:
                break

        if error_occur == True:
            return Response(
                response=json.dumps({
                    "reason": "This email have already existed try new one!"
                }),
                status=400,
                mimetype=f"{constants.normal_from}",
            )

        encode_password = algorithm.encode_main(password, 'na')
        new_account = {
            "username": username,
            "password": encode_password
        }
        db.account.insert_one(new_account)

        return Response(
            response=json.dumps({
                "message": "New Account Created Success"
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )
    except error:
        print('Error at new_account(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )

#######################################################################


@app.route("/account/password-recover", methods=[constants.patch])
def update_password():
    try:
        # request.get_json = equal to req.body in nodejs
        body = request.get_json()
        username = body['username']
        password = body['password']

        record = db.account.find_one({"username": username})
        if record == None:
            return Response(
                response=json.dumps({
                    "reason": "This email haven't existed in our database, register instead"
                }),
                status=400,
                mimetype=f"{constants.normal_from}",
            )

        new_password = algorithm.encode_main(password, 'na')

        db.account.update_one(
            {"_id": record['_id']},
            {"$set": {"password": new_password}}
        )

        return Response(
            response=json.dumps({
                "message": "Recover password",
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )
    except error:
        print('Error at update_password(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )


#######################################################################
if __name__ == "__main__":
    app.run(port=constants.get_port(), debug=True)
