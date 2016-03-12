# misc resources for extra features

from flask_restful import Resource, abort, reqparse

from edx_adapt.data.interface import DataException
from edx_adapt.select.interface import SelectException



bo_parser = reqparse.RequestParser()
bo_parser.add_argument('parameters', type=dict, required=True, location='json', help="Please supply parameters from BO")
bo_parser.add_argument('course_id', type=str, required=True, location='json', help="Please supply a course ID")

class PostBOParameters(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def post(self):
        args = bo_parser.parse_args()
        try:
            self.repo.set('NEXT_BO_PARAMS_' + args['course_id'], args['parameters'])
        except DataException as e:
            abort(500, message=str(e))

        return {'success': True}, 200

class LoadBOParamsForUser(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']
        """@type repo: DataInterface"""
        """@type selector: SelectInterface"""

    def get(self, course_id, user_id):
        params = self.repo.get('NEXT_BO_PARAMS_' + course_id)
        for skill, param in params.iteritems():
            self.selector.set_parameter(param, course_id, user_id, skill)
        self.repo.set('NEXT_BO_PARAMS_' + course_id, None)
        return {'success': True}, 200

    def post(self, course_id, user_id):
        self.get(course_id, user_id)
        return {'success': True}, 200



hitid_parser = reqparse.RequestParser()
hitid_parser.add_argument('hitid', type=dict, required=True, location='json', help="Please supply hit ID")

class HitID(Resource):
    def __init(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']
        """@type repo: DataInterface"""
        """@type selector: SelectInterface"""

    def post(self):
        args = hitid_parser.parse_args()
        self.repo.set("__HITID__", args['hitid'])
        return {'success': True}, 200

    def get(self):
        hitid = self.repo.get("__HITID__")
        return {'hitid': hitid}, 200
