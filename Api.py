from flask import Flask, request, jsonify,render_template
import os


os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():

    return render_template("index.html")





app.run()