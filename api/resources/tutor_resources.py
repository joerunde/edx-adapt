""" This file contains api resources for interacting with the tutor
as users take the course.
"""

import time, threading
from flask_restful import Resource, abort, reqparse
from ...data.interface import DataInterface, DataException
#from ...select.interface import SelectInterface

""" Handle request for user's current and next problem """
class UserProblems(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def get(self, course_id, user_id):
        try:
            next = self.repo.get_next_problem(course_id, user_id)
            cur = self.repo.get_current_problem(course_id, user_id)
        except DataException as e:
            abort(404, message = e.message)

        return {"next": next, "current": cur}


""" Argument parser for posting a user response """
result_parser = reqparse.RequestParser()
result_parser.add_argument('problem', type=str, required=True,
                           help="Must supply the name of the problem which the user answered")
result_parser.add_argument('correct', type=int, required=True,
                           help="Must supply correctness, 0 for incorrect, 1 for correct")
result_parser.add_argument('attempt', type=int, required=True,
                           help="Must supply the attempt number, starting from 1 for the first attempt")
result_parser.add_argument('unix_seconds', type=int, help="Optionally supply timestamp in seconds since unix epoch")
result_parser.add_argument('done', type=bool, required=True,
                           help="Legacy support for multiple part problems. Supply false if"
                                " the user must answer more parts, otherwise leave this true")

""" Global lock for calling choose_next_problem """
selector_lock = threading.Lock()

""" Run the problem selection sequence (in separate thread) """
def run_selector(course_id, user_id, selector, repo):
    with selector_lock:
        #"""@type selector: SelectInterface"""
        """@type repo: DataInterface"""
        next = repo.get_next_problem(course_id, user_id)

        #only run if no next problem has been selected yet
        if next == None:
            selector.choose_next_problem(course_id, user_id)

""" Post a user's response to their current problem """
class UserInteraction(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def post(self, course_id, user_id):
        args = result_parser.parse_args()
        if args['unix_seconds'] == None:
            args['unix_seconds'] = int(time.time())

        try:
            # If this is a response to the "next" problem, advance to it first before storing
            if args['problem'] == self.repo.get_next_problem(course_id, user_id):
                self.repo.advance_problem(course_id, user_id)

            self.repo.post_interaction(course_id, args['problem'], user_id, args['correct'],
                                       args['attempt'], args['unix_seconds'])

            # if the user needs a new problem, start choosing one
            if args['done']:
                try:
                    threading.Thread(target=run_selector, args=(course_id, user_id))
                except Exception as e:
                    abort(500, message="Interaction successfully stored, but an error occurred starting "
                                       "a problem selection thread: " + e.message)
        except DataException as e:
            abort(500, message=e.message)

        return {"success": True}, 200

load_parser = reqparse.RequestParser()
load_parser.add_argument('problem', required=True, help="Must supply the name of the problem loaded")
load_parser.add_argument('unix_seconds', type=int, help="Optionally supply timestamp in seconds since unix epoch")

""" Post the time when a user loads a problem. Used to log time spent solving a problem """
class UserPageLoad(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def post(self, course_id, user_id):
        args = load_parser.parse_args()
        if args['unix_seconds'] == None:
            args['unix_seconds'] = int(time.time())

        try:
            self.repo.post_load(course_id, args['problem'], user_id, args['unix_seconds'])
            if args['problem'] == self.repo.get_next_problem(course_id, user_id):
                self.repo.advance_problem(course_id, user_id)
        except DataException as e:
            abort(500, message=e.message)

        return {"success": True}, 200