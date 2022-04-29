from flask import Flask, Response, request
from pymongo import MongoClient
from flask_cors import CORS, cross_origin

from PIL import Image, ImageDraw, ImageFont
import RSA

import common.constants as constants
import common.hash as algorithm
import common.decode as solver
import json
import os
import cloudinary
import cloudinary.uploader as uploader


app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = './upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cloudinary.config(cloud_name=constants.cloudinary_name,
                  api_key=constants.cloudinary_api_key, api_secret=constants.cloudinary_api_secret)

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

@app.route("/account/get-all-encode", methods=[constants.get])
@cross_origin()
def get_encode():
    try:
        body = request.get_json()
        resource_type = body['type']
        user_id = body['userId']
        output = []

        db_records = list(db.encode.find(
            {"type": resource_type, "userId": user_id}))

        for record in db_records:
            output.append(record['data'])

        return Response(
            response=json.dumps({
                "result": output
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )

    except error:
        print('Error at get_encode(): ', error)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{error}"
            }),
        )


#######################################################################

# FOR THE ENCRYPTIONS

def add_water_mark(path, text_to_add):
    image = Image.open(path)
    watermark_image = image.copy()

    draw = ImageDraw.Draw(watermark_image)

    #choose a font and size
    font = ImageFont.truetype("arial.ttf", 50)

    #add water mark
    position = (25, 25)
    color = (0,0,0)

    draw.text(position, text_to_add, color, font=font)
    
    return watermark_image




@app.route("/account/encode-picture", methods=[constants.post])
@cross_origin()
def file_receiver():
    try:
        # step one: get picture from request
        picture = request.files.get('image')
        user_id = request.form.get('userId')
        water_mark = request.form.get('waterMark')
        app.logger.info(water_mark)
        path = os.path.join(app.config['UPLOAD_FOLDER'], picture.filename)
        picture.save(path)

        #Add the water mark
        img = add_water_mark(path, water_mark)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], picture.filename))
        img.save(path)

        # step two: encode picture then upload to cloudinary database
        # TODO: encode part start here
        upload_result = uploader.upload(path)
        image_link = upload_result.get('url')
        print("Image Link:", image_link)

        #RSA
        #public_key, private_key = RSA.generate_keys()
        # print("Public key:", public_key)
        # print("Private key:", private_key)

        #image_link_encoded = RSA.encode(image_link, public_key)

        # encode part end here

        # step three: store it to database
        # if user_id != "none" or user_id != None:
        #     insert_info = {
        #         "type": "image",
        #         "userId": user_id,
        #         "data": image_link
        #     }
        #     db.encode.insert_one(insert_info)

        # step four: remove local image due to performance
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], picture.filename))

        return Response(
            response=json.dumps({
                "imageLink": image_link,
                #"privateKey" : private_key
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )

    except error:
        print('Error at file_receiver(): ', error)
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
