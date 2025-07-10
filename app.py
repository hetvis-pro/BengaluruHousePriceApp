from flask import Flask, request, jsonify, render_template
import json
import pickle
import numpy as np
import os

app = Flask(__name__)

__locations = None
__data_columns = None
__model = None

def load_saved_artifacts():
    global __data_columns
    global __locations
    global __model

    print("Loading saved model and columns...")

    with open(os.path.join("model", "columns.json"), "r") as f:
        __data_columns = json.load(f)["data_columns"]
        __locations = __data_columns[3:]

    with open(os.path.join("model", "bangalore_home_prices_model.pickle"), "rb") as f:
        __model = pickle.load(f)

    print("Model & columns loaded!")


def get_location_names():
    return __locations


def get_estimated_price(location, sqft, bhk, bath):
    try:
        loc_index = __data_columns.index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index >= 0:
        x[loc_index] = 1

    return round(__model.predict([x])[0], 2)


@app.route("/get_location_names")
def get_location_names_route():
    response = jsonify({
        "locations": get_location_names()
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/predict_home_price", methods=["POST"])
def predict_home_price():
    total_sqft = float(request.form["total_sqft"])
    location = request.form["location"]
    bhk = int(request.form["bhk"])
    bath = int(request.form["bath"])

    response = jsonify({
        "estimated_price": get_estimated_price(location, total_sqft, bhk, bath)
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/")
def home():
    return render_template("app.html")

if __name__ == "__main__":
    load_saved_artifacts()
    print("Starting Flask server for Bengaluru House Price Prediction...")
    app.run(debug=True)
