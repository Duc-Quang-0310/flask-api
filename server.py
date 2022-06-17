from tokenize import Name
from flask import Flask, Response, request
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import RSA
import common.constants as constants
import common.hash as algorithm
import common.decode as solver
import json
import os
import cloudinary
import cloudinary.uploader as uploader
import common.watermark as watermark
from PIL import Image, ImageDraw, ImageFont
import Ceaser_cipher as cipher

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
    except NameError:
        print('Error at logging(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
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
    except NameError:
        print('Error at new_account(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
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
    except NameError:
        print('Error at update_password(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
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

    except NameError:
        print('Error at get_encode(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
            }),
        )


#######################################################################

# FOR THE ENCRYPTIONS

def addWaterMark(imgLink, text):
    base = Image.open(imgLink).convert('RGBA')
    width, height = base.size

    # make a blank image for the text, initialized to transparent text color
    txt = Image.new('RGBA', base.size, (255, 255, 255, 0))

    # get a font
    fnt = ImageFont.truetype('arial.ttf', 70)
    # get a drawing context
    d = ImageDraw.Draw(txt)

    x = 80
    y = height/2

    # draw text, half opacity
    d.text((x, y), text, font=fnt, fill=(255, 255, 255, 180))
    txt = txt.rotate(30)

    out = Image.alpha_composite(base, txt)
    return out


@app.route("/account/encode-picture", methods=[constants.post])
@cross_origin()
def file_receiver():

    try:
        # step one: get picture from request
        picture = request.files.get('image')
        user_id = request.form.get('userId')
        water_mark = request.form.get('waterMark')

        path = os.path.join(
            app.config['UPLOAD_FOLDER'], picture.filename + '.png')
        picture.save(path)

        # Add the water mark
        img = addWaterMark(path, water_mark)
        img.save(path)

        # step two: encode picture then upload to cloudinary database
        upload_result = uploader.upload(path)
        image_link = upload_result.get('url')

        # step three: store it to database
        if user_id != "none" or user_id != None:
            insert_info = {
                "type": "image",
                "userId": user_id,
                "data": image_link
            }
            db.encode.insert_one(insert_info)

        # step four: remove local image due to performance
        os.remove(os.path.join(
            app.config['UPLOAD_FOLDER'], picture.filename + '.png'))

        return Response(
            response=json.dumps({
                "imageLink": image_link,
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )

    except NameError:
        print('Error at file_receiver(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
            }),
        )

#######################################################################


@app.route("/account/encode-text", methods=[constants.post])
def encode_text():
    try:
        body = request.get_json()
        text = body['text']
        key = body['key']
        print(text)
        print(key)
        k = int(key)

        encoded_msg = cipher.ceaser_encrypt(text, k)

        return Response(
            response=json.dumps({
                "string": encoded_msg
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )

    except NameError:
        print('Error at file_receiver(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
            }),
        )

#######################################################################


@app.route("/account/decode-text", methods=[constants.post])
def decode_text():
    try:
        body = request.get_json()
        text = body['text']
        key = body['key']
        print(text)
        print(key)
        k = int(key)

        decoded_msg = cipher.ceaser_decrypt(text, k)

        return Response(
            response=json.dumps({
                "string": decoded_msg
            }),
            status=200,
            mimetype=f"{constants.normal_from}",
        )

    except NameError:
        print('Error at decode_text(): ', NameError.name)
        return Response(
            status=500,
            mimetype=f"{constants.normal_from}",
            response=json.dumps({
                "message": f"{constants.internal_server_error}",
                "reason": f"{NameError.name}"
            }),
        )


#######################################################################
if __name__ == "__main__":
    app.run(port=constants.get_port(), debug=True)
