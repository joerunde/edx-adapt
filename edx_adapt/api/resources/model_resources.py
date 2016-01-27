""" This file contains api resources for setting model parameters for a course
"""

from flask_restful import Resource, abort, reqparse

from edx_adapt.data.interface import DataException
from edx_adapt.select.interface import SelectException

param_parser = reqparse.RequestParser()
param_parser.add_argument('course_id', type=str, loation='json', help="Optionally supply a course id")
param_parser.add_argument('user_id', type=str, location='json', help="Optionally supply a user ID")
param_parser.add_argument('skill_name', type=str, location='json', help="Optionally supply the name of a skill")
param_parser.add_argument('params', type=dict, location='json', required=True,
                          help="Please supply the desired model parameters as a dictionary")

class Parameters(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']
        """@type repo: DataInterface"""
        """@type selector: SelectInterface"""

    def get(self):
        param_list = []
        try:
            #get_all_params not even in the interface yet, lol
            param_list = self.selector.get_all_parameters()
        except SelectException as e:
            abort(500, message=str(e))
        return {'parameters': param_list}, 200

    def post(self):
        args = param_parser.parse_args()
        course = args['course_id']
        user = args['user_id']
        skill = args['skill_name']
        params = args['params']

        try:
            self.selector.set_parameter(params, course, user, skill)
        except SelectException as e:
            abort(500, message=str(e))

        return {'success': True}, 200
