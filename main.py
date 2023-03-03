import random

import sqlalchemy
from sqlalchemy import exc
import werkzeug
from werkzeug import exceptions
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.app_context().push()

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# db.create_all()
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    random_cafe = random.choice(Cafe.query.all())
    cafe_dict = {column.name: getattr(random_cafe, column.name) for column in random_cafe.__table__.columns}
    return jsonify({"cafe": cafe_dict})


## HTTP GET - Read Record
@app.route("/all")
def all_cafe():
    cafes_list = Cafe.query.all()
    cafes_list_data = []
    for cafe in cafes_list:
        cafe_dict = {column.name: getattr(cafe, column.name) for column in cafe.__table__.columns}
        cafes_list_data.append(cafe_dict)
    return jsonify({"Cafes": cafes_list_data})


@app.route("/search")
def search():
    try:
        location = request.values['loc'].title()
    except werkzeug.exceptions.BadRequestKeyError:
        return jsonify({"error": {"Invalid": f"Please Enter a valid url"}})
    user_search_cafe = Cafe.query.filter_by(location=location).all()

    if not user_search_cafe:
        return jsonify({"error": {"Not Found": f"Sorry we don't have at location {location}"}})
    user_search_cafe_list = []
    for cafe in user_search_cafe:
        user_search_cafe_dict = {column.name: getattr(cafe, column.name) for column in cafe.__table__.columns}
        user_search_cafe_list.append(user_search_cafe_dict)
    return jsonify({"Cafe": user_search_cafe_list})


## HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.values['name'],
        map_url=request.values['map_url'],
        img_url=request.values['img_url'],
        location=request.values['location'],
        seats=request.values['seats'],
        has_toilet=True if request.values['has_toilet'] == "True" else False,
        has_wifi=True if request.values['has_wifi'] == "True" else False,
        has_sockets=True if request.values['has_sockets'] == "True" else False,
        can_take_calls=True if request.values['can_take_calls'] == "True" else False,
        coffee_price=request.values['coffee_price'],
    )
    try:
        db.session.add(new_cafe)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return jsonify(response={"Fail": "Repeat."})

    return jsonify(response={"Success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_cafe_price(cafe_id):
    cafe_to_update_price = Cafe.query.get(cafe_id)
    if not cafe_to_update_price:
        return jsonify(response={"Fail": "Invalid ID."}), 404
    cafe_to_update_price.coffee_price = request.values['coffee_price']
    db.session.commit()

    return jsonify(response={"SUCCESS": f"PRICE UPDATED SUCCEFFULLY for {cafe_to_update_price.name}"})
## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.values['api-key'] == "TopSecretAPIKey":
        cafe_to_delete = Cafe.query.get(cafe_id)
        if not cafe_to_delete:
            return jsonify(WRONG_ID={"Fail": "Invalid ID."}), 404
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(DELETED={"SUCCESS": "Successfully Deleted."})

    return jsonify(WRONG_API_KEY={"Fail": "Invalid API KEY."}), 403


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
