""" This file contains api resources for serving data from the course.
Currently this is for downloading user response data, but this could be
extended for viewing model parameter data in a web gui, etc.
"""



from flask_restful import Resource, abort, reqparse

from edx_adapt.data.interface import DataException
from edx_adapt.select.interface import SelectException

""" Handle request for a user's log on one problem """
class SingleProblemRequest(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        """@type repo: DataInterface"""

    def get(self, course_id, user_id, problem_name):
        problog = []
        try:
            log = self.repo.get_raw_user_data(course_id, user_id)
            problog = [x for x in log if x['problem']['problem_name'] == problem_name]
        except DataException as e:
            abort(500, message=str(e))
        return {'log': problog}

#TODO: literally everything else
#serve raw log, and trajectories (whole and split by skill)
#serve by user, by all finished users, and by experiment
#(maybe later by date)

