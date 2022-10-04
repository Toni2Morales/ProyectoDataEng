from flask import Flask, request, render_template, jsonify, redirect
import os
import pickle
import pandas as pd 
from sklearn.metrics import mean_absolute_error as MAE
#import pymysql
import pandas as pd
from os import environ
# os.chdir(os.path.dirname(__file__))
app = Flask(__name__)
import json
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import sqlite3



os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOlDER"]="static/files"

@app.route("/", methods=['GET'])
def hello():

    return render_template("index.html")

@app.route("/v1", methods=['GET'])
def datos_predion():

    return render_template("predict.html")

class UploadFileForm(FlaskForm):
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Upload File")
    
@app.route('/ingest', methods=['GET',"POST"])
def new_data():
    form = UploadFileForm()
    if form.validate_on_submit():
        # First grab the file
        file = form.file.data 
        # Save the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOlDER'],secure_filename(file.filename))) # Then save the file

        # Open file
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)))+"/static/files/"+file.filename,'r') as f:
            data = json.loads(f.read())

        # Flatten data
        # usuario = "admin"
        # contrasena = "789123456"
        # host = "dataeng.clev5oqi6ti6.us-east-2.rds.amazonaws.com"
        # conexion = pymysql.connect(user = usuario, password=contrasena, host = host, cursorclass = pymysql.cursors.DictCursor)
        # RDS = conexion.cursor()
        # RDS.execute("use players_database")
        # RDS.execute("select * from players_table")

        new_data_df = pd.json_normalize(data)
        sql = sqlite3.connect('players.db')
        cursor = sql.cursor()

        lista_valores = new_data_df.values.tolist()
        instruccion = "INSERT INTO players VALUES {uno}, {dos}, {tres}, {cuatro}".format(uno = tuple(lista_valores[0]), dos = tuple(lista_valores[1]), tres = tuple(lista_valores[2]), cuatro = tuple(lista_valores[3]))
        cursor.execute(instruccion)
        sql.commit()
        sql.close()
        return redirect("/monitorizar")

    return render_template('ingest.html', form=form)

@app.route("/monitorizar", methods=['GET'])
def monitorizar():
    data2 = pd.read_json("static/files/dato2.json")
    with open("model", "rb") as f:
        modelo = pickle.load(f)
    x2 = data2.drop(columns = "overall_rating")
    y2 = data2["overall_rating"]
    score2 = MAE(y2, modelo.predict(x2))
    jason= pd.read_json("score1.json")
    score1 = jason.iloc[0][0]
    resultado = ""
    if score1 < score2:
        resultado =  redirect(reentrenar())
    return str(resultado + "la monitorización fue realizada")

@app.route("/reentrenar", methods=['GET'])
def reentrenar():

    sql = sqlite3.connect('players.db')
    cursor = sql.cursor()
    DataTotal = pd.DataFrame(cursor.execute("select * from players").fetchall(), columns = ['potential', 'finishing', 'short_passing', 'volleys', 'dribbling',
    'long_passing', 'ball_control', 'reactions', 'shot_power', 'long_shots','interceptions', 'positioning', 'vision', 'standing_tackle',
    'sliding_tackle', 'overall_rating'])
    X = DataTotal.drop(columns = "overall_rating")
    Y = DataTotal["overall_rating"]
    with open("model", "rb") as f:
        modelo = pickle.load(f)
    modelo.fit(X, Y)
    jason= pd.read_json("score1.json")
    SCORE1 = jason.iloc[0][0]
    SCORE2 = MAE(Y, modelo.predict(X))
    SiNo = ""
    if SCORE2 < SCORE1:
        SiNo = "El modelo ha sido reentrenado y "
        with open("model", "wb") as g:
            pickle.dump(modelo, g)
    return SiNo

@app.route('/predict', methods=['GET'])

def predict():
    model = pickle.load(open('model','rb'))

    potential = float(request.args.get('potential', None))
    finishing = float(request.args.get('finishing', None))
    short_passing = float(request.args.get('short_passing', None))
    volleys = float(request.args.get('volleys', None))
    dribbling = float(request.args.get('dribbling', None))
    long_passing = float(request.args.get('long_passing', None))
    ball_control = float(request.args.get('ball_control', None))
    reactions = float(request.args.get('reactions', None))
    shot_power = float(request.args.get('shot_power', None))
    long_shots = float(request.args.get('long_shots', None))
    interceptions = float(request.args.get('interceptions', None))
    positioning = float(request.args.get('positioning', None))
    vision = float(request.args.get('vision', None))
    standing_tackle = float(request.args.get('standing_tackle', None))
    sliding_tackle = float(request.args.get('sliding_tackle', None))
    
    prediction = model.predict([[potential,finishing,short_passing,volleys,dribbling,long_passing,ball_control,reactions,
                                shot_power,long_shots,interceptions,positioning,vision,standing_tackle,sliding_tackle]])
    return render_template('predict.html', predict='La predicción es :  {}'.format(prediction))


@app.route("/ultimo_registro", methods=['GET'])

def ultimo_registro():
    connection = sqlite3.connect('players.db')
    cursor = connection.cursor()
    select_datos = "SELECT * FROM players"
    result = cursor.execute(select_datos).fetchall() 
    connection.close()
    return jsonify(result[-10:]) 
    
if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0', port=environ.get("PORT", 5000))
