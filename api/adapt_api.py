from flask import Flask
from flask.ext.cors import CORS
from flask_restful import Resource, Api


app = Flask(__name__)
CORS(app)
api = Api(app)






#@app.route('/')
#def hello_world():
#    return 'Hello World!'


if __name__ == '__main__':
    app.run()
