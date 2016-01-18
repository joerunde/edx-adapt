import flask
from flask import Flask
from flask.ext.cors import CORS
from flask_restful import Api

# import API resources
import resources.course_resources as CR
import resources.tutor_resources as TR
# import data module
import edx_adapt.data.tinydbRepository as repo

app = Flask(__name__)
CORS(app)
api = Api(app)

# TODO: load from settings
base = '/api/v1'

data = repo.TinydbRepository('/tmp/2.json')

api.add_resource(CR.Courses, base + '/course',
                 resource_class_kwargs={'data': data})
api.add_resource(CR.Skills, base + '/course/<course_id>/skill',
                 resource_class_kwargs={'data': data})
api.add_resource(CR.Users, base + '/course/<course_id>/user',
                 resource_class_kwargs={'data': data})
api.add_resource(CR.Problems, base + '/course/<course_id>', base + '/course/<course_id>/skill/<skill_name>',
                 resource_class_kwargs={'data': data})

api.add_resource(TR.UserInteraction, base + '/course/<course_id>/user/<user_id>/interaction',
                 resource_class_kwargs={'data': data})
api.add_resource(TR.UserProblems, base + '/course/<course_id>/user/<user_id>',
                 resource_class_kwargs={'data': data})
api.add_resource(TR.UserPageLoad, base + '/course/<course_id>/user/<user_id>/pageload',
                 resource_class_kwargs={'data': data})


@app.errorhandler(404)  # Return JSON with 404 instead of html
def page_not_found(e):
    return flask.jsonify(error=404, text=str(e)), 404


def run():
    app.run(debug=True, port=9000)

if __name__ == '__main__':
    app.run()
