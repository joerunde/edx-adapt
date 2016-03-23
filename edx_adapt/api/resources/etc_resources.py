# misc resources for extra features

from flask_restful import Resource, abort, reqparse
from flask import Response

from edx_adapt.data.interface import DataException
from edx_adapt.select.interface import SelectException
import edx_adapt.misc.psiturk_with_bo

import time, datetime, thread

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
            self.repo.set('NEXT_BO_PARAMS_USERS_' + args['course_id'], [])
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
        try:
            #was anybody else using these?
            prev_users = self.repo.get('NEXT_BO_PARAMS_USERS_' + course_id)
            if len(prev_users) > 0:
                fin = self.repo.get_finished_users(course_id)
                for user in prev_users:
                    if user in fin:
                        append_to_log("CRAP! BIG ERROR! " + user_id + " IS REUSING THE SAME PARAMETERS AS "
                                      + user + "!", self.repo)
            prev_users.append(user_id)
            self.repo.set('NEXT_BO_PARAMS_USERS_' + course_id, prev_users)

            params = self.repo.get('NEXT_BO_PARAMS_' + course_id)
            for skill, param in params.iteritems():
                self.selector.set_parameter(param, course_id, user_id, skill)

        except SelectException as e:
            abort(500, message=str(e))
        except DataException as e:
            abort(500, message=str(e))
        return {'success': True}, 200

    def post(self, course_id, user_id):
        self.get(course_id, user_id)
        return {'success': True}, 200

hitid_parser = reqparse.RequestParser()
hitid_parser.add_argument('hitid', type=dict, required=True, location='json', help="Please supply hit ID")

class HitID(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']
        """@type repo: DataInterface"""
        """@type selector: SelectInterface"""

    def post(self):
        try:
            args = hitid_parser.parse_args()
            self.repo.set("__HITID__", args['hitid'])
        except DataException as e:
            abort(500, message=str(e))
        return {'success': True}, 200

    def get(self):
        hitid = ''
        try:
            hitid = self.repo.get("__HITID__")
        except DataException as e:
            abort(500, message=str(e))
        return {'hitid': hitid}, 200

#Because I'm lazy and want to just type in a hitID in a browser without using url params or specifying a post
class EZHitIDSetter(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']
        """@type repo: DataInterface"""
        """@type selector: SelectInterface"""

    def get(self, hitid):
        # This is really a post
        self.repo.set("__HITID__", hitid)
        return {'success': True}

log_parser = reqparse.RequestParser()
log_parser.add_argument('log', type=str, required=True, location='json', help="Please supply something to log")

#utility fn for local use
def append_to_log(log, repo):
    try:
        old_log = repo.get("__SUMMARY_LOG__")
    except DataException as e:
        old_log = "<html>either an error happened, or this is the start of the log</br>"
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    new_log = old_log + "</br></br>" + timestamp + "</br>" + log
    repo.set("__SUMMARY_LOG__", new_log)

#endpoint for logging events related to the tutor->bayesian optimization->turk->enrollment loop
#so that we can tell when things go sideways
class LoopLog(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']

    def post(self):
        try:
            log = log_parser.parse_args()['log']
            print log
            append_to_log(log, self.repo)
        except DataException as e:
            abort(500, message=str(e))

        return {'success': True}, 200

    def get(self):
        log = ''
        try:
            log = self.repo.get("__SUMMARY_LOG__")
        except DataException as e:
            abort(500, message=str(e))
        return Response(log, mimetype="text/html")

class ClearLog(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']

    def get(self):
        try:
            self.repo.set("__SUMMARY_LOG__", "<html>")
        except DataException as e:
            abort(500, message=str(e))
        return {'success': True}, 200

class HitChecker5000(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']

    def get(self, course_id):
        extend = edx_adapt.misc.psiturk_with_bo.psiturk_hit_check(self.repo)
        if extend:
            edx_adapt.misc.psiturk_with_bo.set_next_users_parameters(self.repo, self.selector, course_id)
            return {'message': 'starting...'}, 200
        return {'message': 'no hit extend needed.'}, 200

class BOPoints(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']

    def get(self, course_id):
        traj = []
        params = []
        try:
            exps = self.repo.get_experiments(course_id)
            now = int(time.time())
            exp = None
            for e in exps:
                if e['start_time'] < now and e['end_time'] > now:
                    exp = e
            if exp is None:
                append_to_log("NO current experiment found for Bayesian Optimization on course: " + course_id + ". Cannot find BO points.", self.repo)
                return {'message': "No experiment found for BO"}, 500
            #get list of skills up in this business
            skills = self.repo.get_skills(course_id)
            if 'None' in skills:
                skills.remove('None')
            users = self.repo.get_subjects(course_id, exp['experiment_name'])
            blobs = edx_adapt.misc.psiturk_with_bo.get_blobs_with_params(self.repo, self.selector, course_id, users, skills)
            traj, params = edx_adapt.misc.psiturk_with_bo.transform_blobs_for_BO(blobs)
        except DataException as e:
            abort(500, message=str(e))
        except SelectException as e:
            abort(500, message=str(e))

        points = (traj, params)
        return {'BO_points': points}, 200



borun_parser = reqparse.RequestParser()
borun_parser.add_argument('trajectories', type=dict, required=True, location='json', help="Please supply previous trajectories")

#endpoint to just run BO
class BORunner(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']

    def post(self, course_id):
        # not getting anything, just asking for another loop to start
        args = borun_parser.parse_args()
        trajectories = args['trajectories']
        thread.start_new_thread(edx_adapt.misc.psiturk_with_bo.run_BO, (trajectories, course_id))
        return {'message': 'starting...'}, 200

#endpoint for admins to hit to start up another BO+Turk loop if things go sideways (as they're want to do)
class LoopRunner(Resource):
    def __init__(self, **kwargs):
        self.repo = kwargs['data']
        self.selector = kwargs['selector']

    def get(self, course_id):
        # not getting anything, just asking for another loop to start
        edx_adapt.misc.psiturk_with_bo.set_next_users_parameters(self.repo, self.selector, course_id)
        return {'message': 'starting...'}, 200