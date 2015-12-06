""" This file contains api resource classes dealing with course information.
For example, CRUDding courses, users, problems, skills...
"""

from flask_restful import Resource, abort, reqparse

from edx_adapt.data import DataException

course_parser = reqparse.RequestParser()
course_parser.add_argument('course_id', type=str, required=True, help="Please supply a course ID")


class Courses(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def get(self):
        courses = []
        try:
            courses = self.repo.get_course_ids()
        except DataException as e:
            abort(500, message=e.message)
        return {'course_ids': courses}, 200

    def post(self):
        args = course_parser.parse_args()
        try:
            self.repo.post_course(args['course_id'])
        except DataException as e:
            abort(500, message=e.message)

        return {'success': True}, 200


skill_parser = reqparse.RequestParser()
skill_parser.add_argument('skill_name', type=str, required=True, help="Please supply the name of a skill")


class Skills(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def get(self, course_id):
        skills = []
        try:
            skills = self.repo.get_skills(course_id)
        except DataException as e:
            abort(500, message=e.message)

        return {'skills': skills}, 200

    def post(self, course_id):
        args = skill_parser.parse_args()
        try:
            self.repo.post_skill(course_id, args['skill_name'])
        except DataException as e:
            abort(500, message=e.message)

        return {'success': True}, 200


user_parser = reqparse.RequestParser()
user_parser.add_argument('user_id', type=str, required=True, help="Please supply a user ID")


class Users(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def get(self, course_id):
        finished_users = []
        progress_users = []
        try:
            finished_users = self.repo.get_finished_users(course_id)
            progress_users = self.repo.get_in_progress_users(course_id)
        except DataException as e:
            abort(500, message=e.message)

        return {'users': {'finished': finished_users, 'in_progress': progress_users}}, 200

    def post(self, course_id):
        args = user_parser.parse_args()
        try:
            self.repo.enroll_user(course_id, args['user_id'])
        except DataException as e:
            abort(500, message=e.message)

        return {'success': True}, 200


problem_parser = reqparse.RequestParser()
problem_parser.add_argument('problem_name', type=str, required=True, help="Please supply a problem name")
problem_parser.add_argument('tutor_url', type=str, required=True,
                            help="Please supply a link to the problem's page in your tutor")
problem_parser.add_argument('skills', type=list, required=True,
                            help="Please supply a list of skills that this problem teaches")
problem_parser.add_argument('pretest', type=bool,
                            help="Set True if this is a pretest problem. Mutually exclusive with posttest")
problem_parser.add_argument('posttest', type=bool,
                            help="Set True if this is a posttest problem. Mutually exclusive with pretest")

class Problems(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def get(self, course_id, skill_name):
        problems = []
        try:
            problems = self.repo.get_problems(course_id, skill_name)
        except DataException as e:
            abort(500, message=e.message)

        return {'problems': problems}, 200

    def post(self, course_id):
        args = problem_parser.parse_args()
        try:
            if args['pretest']:
                self.repo.post_pretest_problem(course_id, args['skills'], args['problem_name'], args['tutor_url'])
            elif args['posttest']:
                self.repo.post_posttest_problem(course_id, args['skills'], args['problem_name'], args['tutor_url'])
            else:
                self.repo.post_problem(course_id, args['skills'], args['problem_name'], args['tutor_url'])
        except DataException as e:
            abort(500, message=e.message)

        return {'success': True}, 200