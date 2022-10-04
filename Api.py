from flask import Flask, request, render_template
import os
import pickle
from sklearn.metrics import mean_absolute_error as MAE
import pymysql
import pandas as pd
from os import environ
# os.chdir(os.path.dirname(__file__))
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():

    return render_template("index.html")


@app.route("/monitorizar", methods=['POST'])
def monitorizar():
    usuario = "admin"
    contrasena = "789123456"
    host = "dataeng.clev5oqi6ti6.us-east-2.rds.amazonaws.com"
    conexion = pymysql.connect(user = usuario, password=contrasena, host = host, cursorclass = pymysql.cursors.DictCursor)
    RDS = conexion.cursor()
    RDS.execute("use players_database")
    RDS.execute("select * from players_table")
    data1 = pd.DataFrame(RDS.fetchall(), columns = ['potential', 'finishing', 'short_passing', 'volleys', 'dribbling',
    'long_passing', 'ball_control', 'reactions', 'shot_power', 'long_shots','interceptions', 'positioning', 'vision', 'standing_tackle',
    'sliding_tackle', 'overall_rating'])
    data2 = pd.DataFrame(request.get_json(), columns = ['potential', 'finishing', 'short_passing', 'volleys', 'dribbling',
    'long_passing', 'ball_control', 'reactions', 'shot_power', 'long_shots','interceptions', 'positioning', 'vision', 'standing_tackle',
    'sliding_tackle', 'overall_rating']).astype("int")
    x = data1.drop(columns = "overall_rating")
    y = data1["overall_rating"]
    with open("model", "rb") as f:
        modelo = pickle.load(f)
    score1 = MAE(y, modelo.predict(x))
    x2 = data2.drop(columns = "overall_rating")
    y2 = data2["overall_rating"]
    score2 = MAE(y2, modelo.predict(x2))
    result = ""
    if score1 < score2:
        result =  reentrenar(x, y, x2, y2)
    return str(" la monitorización fue realizada")

@app.route("/reentrenar", methods=['GET'])
def reentrenar(X,Y, X2, Y2):
    with open("model", "rb") as f:
        modelo = pickle.load(f)
    SCORE1 = MAE(Y2, modelo.predict(X2))
    x3 = pd.concat([X, X2], ignore_index=True)
    y3 = pd.concat([Y, Y2], ignore_index=True)
    modelo.fit(x3, y3)
    SCORE2 = MAE(Y2, modelo.predict(X2))
    SiNo = ""
    if SCORE2 < SCORE1:
        SiNo = "El modelo ha sido reentrenado y "
        with open("model", "wb") as g:
            pickle.dump(modelo, g)
    return SiNo

@app.route("/prediccion", methods=['GET'])
def prediccion():
    data = pd.DataFrame(request.get_json(), columns = ['potential', 'finishing', 'short_passing', 'volleys', 'dribbling',
    'long_passing', 'ball_control', 'reactions', 'shot_power', 'long_shots','interceptions', 'positioning', 'vision', 'standing_tackle',
    'sliding_tackle']).astype("int")
    with open("model", "rb") as f:
        modelo = pickle.load(f)
    pred = modelo.predict(data)
    return "La predicción que ha realizado el modelo con los datos entregados es: " + str(pred)

if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0', port=environ.get("PORT", 5000))