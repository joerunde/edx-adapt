from flask import Flask
from flask.ext.cors import CORS
from flask_restful import Api

# import API resources
import resources.course_resources as CR
# import data module
import edx_adapt.data.mockRepository as mock

app = Flask(__name__)
CORS(app)
api = Api(app)

# TODO: load from settings
base = '/api/v1'

data = mock.MockRepository()

api.add_resource(CR.Courses, base + '/course',
                 resource_class_kwargs={'data': data})
api.add_resource(CR.Skills, base + '/course/<str:course_id>/skill',
                 resource_class_kwargs={'data': data})
api.add_resource(CR.Users, base + '/course/<str:course_id>/user',
                 resource_class_kwargs={'data': data})
api.add_resource(CR.Problems, base + '/course/<str:course_id>', base + '/course/<str:course_id>/skill/<str:skill_name>',
                 resource_class_kwargs={'data': data})


def run():
    app.run()

if __name__ == '__main__':
    app.run()
