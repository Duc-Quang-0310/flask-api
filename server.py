from flask import Flask, Response, request
from pymongo import MongoClient
from bson.objectid import ObjectId

import common.constants as constants
import common.hash as algorithm
import common.decode as solver
import json

app = Flask(__name__)

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
        solver.decode_main(tmp)

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
if __name__ == "__main__":
    app.run(port=constants.get_port(), debug=True)
