# Connect to psiturk to send out hits for users to complete this tutor
# Also use MOE to set user parameters using Bayesian Optimization

USE_PSITURK_AND_BAYESIAN_OPT = True

import sys, os, time, thread, requests
import traceback
import numpy as np
import cPickle
import random
import json
from boto.mturk.connection import MTurkConnection

from moe.optimal_learning.python import bo_edu
from moe.optimal_learning.python.student_objectives import skills_performance_objective_32nd
#sys.modules['bo_edu'] = bo_edu
from moe.optimal_learning.python.bo_edu import BOEDUExperiment, Trajectory, next_moe_pts_edu

from edx_adapt.data.interface import DataInterface
from edx_adapt.data.interface import DataException
from edx_adapt.select.interface import SelectException
from edx_adapt.api.resources.data_serve_resources import fill_user_data
import edx_adapt.api.resources.etc_resources as etc_resources

import SUPER_SECRET_FILE

# connect to turk
#host = 'mechanicalturk.sandbox.amazonaws.com'
host = 'mechanicalturk.amazonaws.com'
mturkparams = dict(aws_access_key_id=SUPER_SECRET_FILE.aws_access_key_id,
                   aws_secret_access_key=SUPER_SECRET_FILE.aws_secret_access_key,
                   host=host)
mturk_conn = MTurkConnection(**mturkparams)

headers = {'Content-type': 'application/json'}

#edx_app host
HOSTNAME = 'cmustats.tk'

def psiturk_hit_check(repo):
    # Okay, the BO params are all loaded (assuming that worked). Now tell psiturk to open another HIT
    hitid = ''
    try:
        hitid = repo.get("__HITID__")
    except Exception as e:
        return False

    hit = None
    try:
        hit, = mturk_conn.get_hit(hitid, ['HITDetail', 'HITAssignmentSummary'])
    except Exception as e:
        return False

    if int(hit.MaxAssignments) >= 9:
        #don't extend more in this case
        return False

    if int(hit.NumberOfAssignmentsAvailable) > 0:
        return False

    return True


def get_blobs_with_params(repo, selector, course, users, skills):
    trajectories = []
    for user in users:
        #get the regular trajectory data from data_serve endpoint utility function
        blob = fill_user_data(repo, course, user)
        #get the model params for this user... (assume doing per-skill params)
        userparams = {}
        for skill in skills:
            if skill == 'None':
                continue
            userparams[skill] = selector.get_parameter(course, user, skill)
            # calc objective
            val = skills_performance_objective_32nd(blob['trajectories']['by_skill'][skill], -1, blob['trajectories']['posttest'], blob['trajectory_skills']['posttest'], skill)
            userparams[skill]['val'] = val

        blob['bo_params_and_results'] = userparams
        trajectories.append(blob)
    return trajectories

def transform_blobs_for_BO(blobs):
    traj = []
    params = []
    for blob in blobs:
        # !!!!!!!!!! pre and post test need to have been given in same order
        blob['trajectories']['test_skills'] = blob['trajectory_skills']['pretest']
        blob['trajectories']['problems_skills'] = blob['trajectory_skills']['problems']
        traj.append(blob['trajectories'])
        for k, v in blob['bo_params_and_results'].iteritems():
            blob['bo_params_and_results'][k]['pl'] = v['pi']
            blob['bo_params_and_results'][k]['th'] = v['threshold']
        params.append(blob['bo_params_and_results'])

    return traj, params

def set_next_users_parameters(repo, selector, course_id):
    # pass here if not using BO
    if not USE_PSITURK_AND_BAYESIAN_OPT:
        print "lol"
        return
    """@type repo: DataInterface """

    etc_resources.append_to_log("Attempting to set next user's parameters for: " + course_id, repo)
    print("Attempting to set next user's parameters for: " + course_id + "\n")

    try:
        #find current experiment
        exps = repo.get_experiments(course_id)

        now = int(time.time())
        exp = None
        for e in exps:
            if e['start_time'] < now and e['end_time'] > now:
                exp = e

        if exp is None:
            etc_resources.append_to_log("NO current experiment found for Bayesian Optimization on course: " + course_id + ". Exiting...", repo)
            print("WOAH! No current experiment found for Bayesian Optimization\n")
            return

        #get list of skills up in this business
        skills = repo.get_skills(course_id)
        if 'None' in skills:
            skills.remove('None')

        users = repo.get_subjects(course_id, exp['experiment_name'])

        #get trajectories
        trajectories = get_blobs_with_params(repo, selector, course_id, users, skills)
        etc_resources.append_to_log(str(len(users)) + " User trajectories found on course: " + course_id + ", running BO on these now.", repo)


        ########## start new thread to run Bayesian Optimization
        # This is important- BO could take a while and the thread running here needs to be serving the REST api
        thread.start_new_thread(run_BO, (trajectories, course_id))

    except DataException as e:
        print(str(e) + "\n")
    except SelectException as e:
        print(str(e) + "\n")
    except Exception as e:
        etc_resources.append_to_log("Crud. Some uncaught exception happened: " + str(e), repo)
        raise e


def remote_log(host, log):
    response = requests.post('http://'+host+':9000/api/v1/misc/log',
                                 data=json.dumps({'log':log}), headers=headers)

def run_BO(blobs, course_id):
    #do a little data shuffling here, need a slightly different format than the web api serves
    traj, params = transform_blobs_for_BO(blobs)

    print("Successfully spun up run_BO thread\n")
    print params

    try:
        print traj

        print params

        next_params = bo_edu.next_moe_pts_edu_stateless_boexpt2(traj, params)[0]

        idx_to_name = bo_edu.SKILL_ID_TO_SKILL_NAME

        tutor_params = {}
        # next_params is a list of lists of parameters
        for c in range(len(next_params)):
            skill = idx_to_name[c]
            x = next_params[c]
            #[pdct["pl"], pdct["pt"], pdct["pg"], pdct["ps"], pdct["th"]]
            params = {'pi': x[0], 'pt': x[1], 'pg': x[2], 'ps': x[3], 'threshold': x[4] }
            tutor_params[skill] = params

        #log the BO result on the server:
        remote_log(HOSTNAME, "Calculated next parameters with BO: " + json.dumps(tutor_params))

        #ping back the server with the new parameters
        response = requests.post('http://'+HOSTNAME+':9000/api/v1/misc/SetBOParams',
                                 data=json.dumps({'course_id':course_id, 'parameters': tutor_params}), headers=headers)
        remote_log(HOSTNAME, "Sent parameters to server, server responded with: " + str(response.json()))

        # Okay, the BO params are all loaded (assuming that worked). Now tell psiturk to open another HIT
        response = requests.get('http://'+HOSTNAME+':9000/api/v1/misc/hitID')
        hitid = ''
        try:
            hitid = response.json()['hitid']
        except Exception as e:
            remote_log(HOSTNAME, "Server error getting response from /hitID. Maybe no HIT ID set? Exiting loop.")
            return

        remote_log(HOSTNAME, "Received HIT ID from server: " + hitid)

        #assignment_list = mturk_conn.get_assignments(hitid)
        hit = None
        try:
            hit, = mturk_conn.get_hit(hitid, ['HITDetail', 'HITAssignmentSummary'])
        except Exception as e:
            remote_log(HOSTNAME, "Error retrieving HIT from mturk, exiting loop: " + str(e))
            return

        print str(hit)
        remote_log(HOSTNAME, "mturk_conn.get_hit() returned: " + str(hit))

        if int(hit.MaxAssignments) >= 9:
            #don't extend more in this case
            remote_log(HOSTNAME, "Maximum number of hits reached (" + str(hit.MaxAssignments) + "), not extending HIT")
            return

        if int(hit.NumberOfAssignmentsAvailable) > 0:
            remote_log(HOSTNAME, "Error, >0 assignments outstanding: (" + str(hit.NumberOfAssignmentsPending) + " pending, " +  str(hit.NumberOfAssignmentsAvailable) + " available), not extending HIT")
            return

        try:
            r = mturk_conn.extend_hit(hitid, assignments_increment=1)
            print str(r)
            remote_log(HOSTNAME, "mturk_conn.extend_hit() returned: " + str(r))
            r = mturk_conn.extend_hit(hitid, expiration_increment=3600 * 3)
            print str(r)
            remote_log(HOSTNAME, "mturk_conn.extend_hit() returned: " + str(r))
        except Exception as e:
            remote_log(HOSTNAME, "Exception extending hit, loop failed: " + str(e))

    except Exception as e:
        remote_log(HOSTNAME, "some other random exception in the loop happened?: " + str(e))
        print "gg, BO broke."
        print(str(e) + "\n")
        print traceback.format_exc()
        raise e
