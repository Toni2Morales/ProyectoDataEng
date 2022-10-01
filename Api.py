from flask import Flask, request, jsonify,render_template
import os
import pickle
from sklearn.metrics import mean_absolute_error as MAE



os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():

    return render_template("index.html")


@app.route("/monitorizar", methods=['GET'])
def monitorizar(data, maeModelo):
    x = data.drop("y")
    y = data["y"]
    with open("modelo", "rb") as f:
        modelo = pickle.load(f)
    score = MAE(y, modelo.predict(x))
    if score > maeModelo:
        reentrenar(data)
    return 

@app.route("/reentrenar", methods=['GET'])
def reentrenar(data):
    x = data.drop(columns = "Y")
    y = data["Y"]
    with open("modelo", "rb") as f:
        modelo = pickle.load(f)
    score1 = MAE(y, modelo.predict(x))
    modelo.fit(x, y)
    score2 = MAE(y, modelo.predict(x))
    if score2 < score1:
        with open("modelo", "wb") as g:
            pickle.dump(modelo, g)
    return

@app.route("/prediccion", methods=['GET'])
def prediccion(data):
    with open("modelo", "rb") as f:
        modelo = pickle.load(f)
    pred = modelo.predict(data)
    return pred
app.run()