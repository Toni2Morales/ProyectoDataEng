from flask import Flask, request, jsonify,render_template
import os
import pickle
import pandas as pd 
from sklearn.metrics import mean_absolute_error as MAE
import json
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import sqlite3



os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOlDER"]="data"

@app.route("/", methods=['GET'])
def hello():

    return render_template("index.html")

@app.route("/v1", methods=['GET'])
def datos_predion():

    return render_template("predict.html")


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

@app.route('/predict', methods=['GET'])

def predict():
    model = pickle.load(open('data/model','rb'))

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
    connection = sqlite3.connect('data/players.db')
    cursor = connection.cursor()
    select_datos = "SELECT * FROM players"
    result = cursor.execute(select_datos).fetchall() 
    connection.close()
    return jsonify(result[-10:]) 


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
        new_data_df = pd.json_normalize(data)

        sql = sqlite3.connect('data/players.db')
        cursor = sql.cursor()

        lista_valores = new_data_df.values.tolist()
        cursor.executemany("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lista_valores)

        sql.commit()
        sql.close()

        return ("Los datos de archivo insertado se ha ingestado en base de datos ")


    return render_template('ingest.html', form=form)


app.run()