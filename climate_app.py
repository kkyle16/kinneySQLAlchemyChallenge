from flask import Flask, jsonify


app = Flask(__name__)

# Provides a list of available routes. Used in the Home route.
def route_list():
    routes = ["/", "/api/v1.0/precipitation", "/api/v1.0/stations", "/api/v1.0/tobs", "/api/v1.0/<start>", "/api/v1.0/<start>/<end>"]
    listing = f"Available Routes:<br>"
    for route in routes:
        listing = listing + f"{route}<br>"
    return listing

@app.route("/")
def home():
    print("Home Page")
    my_list = route_list()
    return (f"Welcome to the Climate App<br>" 
            f"-----------------------------------<br>"
            f"{route_list()}")


@app.route("/api/v1.0/precipitation")
def precip():
    


if __name__ == "__main__":
    app.run(debug=True)