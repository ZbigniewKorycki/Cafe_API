from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
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


with app.app_context():
    db.create_all()


def get_dict(self):
    dictionary = {
        column.name: getattr(self, column.name) for column in self.__table__.columns
    }
    return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(get_dict(random_cafe))


## HTTP GET - Read Record


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return jsonify(cafes=[get_dict(cafe) for cafe in all_cafes])


@app.route("/search")
def search_cafes():
    location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location))
    matching_cafes = result.scalars().all()
    cafes = [get_dict(cafe) for cafe in matching_cafes]
    print(len(cafes))
    if len(cafes) == 0:
        return jsonify(
            error={"Not found": "Sorry we don't have any cafes in this location."}
        )

    else:
        return jsonify(cafes)


## HTTP POST - Create Record


def str_to_bool(arg_from_url):
    if arg_from_url in ["True", "true", "T", "t", "Yes", "yes", "y", "1"]:
        return True
    else:
        return False


@app.route("/add", methods=["POST", "GET"])
def add_new_cafe():
    try:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            seats=request.form.get("seats"),
            has_toilet=str_to_bool(request.form.get("has_toilet")),
            has_wifi=str_to_bool(request.form.get("has_wifi")),
            has_sockets=str_to_bool(request.form.get("has_sockets")),
            can_take_calls=str_to_bool(request.form.get("can_take_calls")),
            coffee_price=request.form.get("coffee_price"),
        )
    except KeyError:
        return jsonify(
            error={"Bad Request": "Some or all fields were incorrect or missing."}
        )
    else:
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"Success": "Successfully added the new cafe"})


## HTTP PUT/PATCH - Update Record


@app.route("/update_price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("coffee_price")
    cafe = db.get_or_404(
        Cafe, cafe_id, description="Bad Request: Cafe with given id, not exist."
    )
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated info"}), 200
    else:
        return jsonify(error={"Bad Request": "Cafe with given id, not exist "}), 404


## HTTP DELETE - Delete Record


@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted cafe."}), 200
        else:
            return jsonify(error={"Not Found": "Cafe with given id not exist"}), 404
    else:
        return (
            jsonify(
                {
                    "error": "You are not allowed to do this, make sure you have a valid api-key"
                }
            ),
            403,
        )


if __name__ == "__main__":
    app.run(debug=True)
