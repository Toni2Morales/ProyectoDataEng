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


app.run()