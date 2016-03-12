# Connect to psiturk to send out hits for users to complete this tutor
# Also use MOE to set user parameters using Bayesian Optimization

USE_PSITURK_AND_BAYESIAN_OPT = True

import sys, os, time, thread, requests
import numpy as np
import cPickle
import random
from boto.mturk.connection import MTurkConnection

from moe.optimal_learning.python import bo_edu
from moe.optimal_learning.python.student_objectives import skills_performance_objective_32nd
#sys.modules['bo_edu'] = bo_edu
from moe.optimal_learning.python.bo_edu import BOEDUExperiment, Trajectory, next_moe_pts_edu

from edx_adapt.data.interface import DataInterface
from edx_adapt.data.interface import DataException
from edx_adapt.select.interface import SelectException
from edx_adapt.api.resources.data_serve_resources import fill_user_data

import SUPER_SECRET_FILE

# connect to turk
# host = 'mechanicalturk.sandbox.amazonaws.com'
host = 'mechanicalturk.amazonaws.com'
mturkparams = dict(aws_access_key_id=SUPER_SECRET_FILE.aws_access_key_id,
                   aws_secret_access_key=SUPER_SECRET_FILE.aws_secret_access_key,
                   host=host)
mturk_conn = MTurkConnection(**mturkparams)


def set_next_users_parameters(repo, selector, course_id):
    # pass here if not using BO
    if not USE_PSITURK_AND_BAYESIAN_OPT:
        return
    """@type repo: DataInterface """

    f = open("turk_logs.txt", "a")
    f.write("\n")
    f.write("Attempting to set next user's parameters for: " + course_id + "\n")

    try:
        #find current experiment
        exps = repo.get_experiments(course_id)

        now = int(time.time())
        exp = None
        for e in exps:
            if e['start_time'] < now and e['end_time'] > now:
                exp = e

        if exp is None:
            f.write("WOAH! No current experiment found for Bayesian Optimization\n")
            return

        #get list of skills up in this business
        skills = repo.get_skills(course_id)

        #get trajectories
        trajectories = []
        users = repo.get_subjects(course_id, exp['experiment_name'])
        for user in users:
            data_dict = fill_user_data(repo, course_id, user)
            #get the regular trajectory data from data_serve endpoint utility function
            blob = fill_user_data(repo, course_id, user)

            #get the model params for this user... (assume doing per-skill params)
            userparams = {}
            for skill in skills:
                userparams[skill] = selector.get_parameter(course_id, user, skill)
                # calc objective
                val = skills_performance_objective_32nd(blob['trajectories']['by_skill'][skill], -1, blob['trajectories']['posttest'], blob['trajectory_skills']['posttest'], skill)
                userparams[skill]['val'] = val

            blob['bo_params_and_results'] = userparams
            trajectories.append(blob)

        ########## start new thread to run Bayesian Optimization
        # This is important- BO could take a while and the thread running here needs to be serving the REST api
        thread.start_new_thread(run_BO, (trajectories, course_id))

    except DataException as e:
        f.write(str(e) + "\n")
    except SelectException as e:
        f.write(str(e) + "\n")
    except Exception as e:
        f.write(str(e) + "\n")

    f.close()


def run_BO(blobs, course_id):
    #do a little data shuffling here, need a slightly different format than the web api serves
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

    f = open("turk_logs.txt", "a")
    f.write("Successfully spun up run_BO thread\n")

    try:

        next_params = bo_edu.next_moe_pts_edu_stateless_boexpt2(traj, params)

        idx_to_name = bo_edu.SKILL_ID_TO_SKILL_NAME

        tutor_params = {}
        # next_params is a list of lists of parameters
        for c in range(len(next_params)):
            skill = idx_to_name[c]
            x = next_params[c]
            #[pdct["pl"], pdct["pt"], pdct["pg"], pdct["ps"], pdct["th"]]
            params = {'pi': x[0], 'pt': x[1], 'pg': x[2], 'ps': x[3], 'th': x[4] }
            tutor_params[skill] = params

        #ping back the server with the new parameters
        response = requests.post('http://cmustats.tk:9000/api/v1/misc/SetBOParams',
                                 data={'course_id':course_id, 'parameters': tutor_params})
        f.write(str(response.json()) + "\n")

        # Okay, the BO params are all loaded (assuming that worked). Now tell psiturk to open another HIT
        response = requests.get('http://cmustats.tk:9000/api/v1/misc/hitID')
        hitid = response.json()['hitid']
        f.write(str(response.json()) + "\n")

        assignment_list = mturk_conn.get_assignments(hitid)
        hit, = mturk_conn.get_hit(hitid, ['HITDetail', 'HITAssignmentSummary'])

        if hit.MaxAssignments >= 9:
            #don't extend more in this case
            f.write("Maximum number of hits reached (" + str(hit.MaxAssignments) + ")\n")
            return

        if int(hit.NumberOfAssignmentsPending) + int(hit.NumberOfAssignmentsAvailable) > 0:
            f.write("FUUUUUUUUUUUUUUUUUUUUUUUUUUCK why is there a hit open?\nlol oh well\n")

        mturk_conn.extend_hit(hitid, assignments_increment=1, expiration_increment=3600 * 3)

    except Exception as e:
        f.write(str(e) + "\n")


"""
def background_function(conn, arg):
    if arg == "best":
        background_process_best(conn)
    elif arg == "start":
        background_process_BO(conn, True)
    elif not arg:
        background_process_BO(conn, False)


def background_process_best(conn):
    # read in static parameters from a file
    params = cPickle.load(open("moe_best_pts.p"))
    while True:
        hitid = open("hitid","r").readline()
        assignment_list = mturk_conn.get_assignments(hitid)
        cur_length = len(assignment_list)
        while True: # wait for the student to start
            assignment_list = mturk_conn.get_assignments(hitid)
            background_state = cPickle.load(open("background_state.p", "rb"))
            if conn.poll():
                received_object = conn.recv()
                if len(received_object) == 1:
                    user_id = received_object[0]
                    print "New User {0}!\n".format(user_id)
                    print "With params: {0}\n\n".format(params)
                    conn.send(params)
                    cPickle.dump(params, open('params_best_' + user_id, 'wb'))
                else:
                    return

            if len(assignment_list) > cur_length:
                hit, = mturk_conn.get_hit(hitid, ['HITDetail', 'HITAssignmentSummary'])
                if int(hit.MaxAssignments) == 9: # Need to wait until new HIT is created
                    print "Waiting for new HIT\n"
                    while open("hitid","r").readline() == hitid: # file hitid has to be changed when new HIT is created
                        time.sleep(60)
                elif int(hit.NumberOfAssignmentsPending) + int(hit.NumberOfAssignmentsAvailable) < 1:
                    print "Extended HIT!\n"
                    mturk_conn.extend_hit(hitid, assignments_increment=1)
                    mturk_conn.extend_hit(hitid, expiration_increment=3600 * 3)
                break

            time.sleep(10)

def background_process_BO(conn, is_new):
    rnd_src = np.random.RandomState(0)
    moe_port = 6543  # default MOE port
    num_skills = 8
    is_bkt = True
    num_lr_extra_params = 1
    edu_expt = BOEDUExperiment(num_skills, is_bkt, num_lr_extra_params, moe_port, rnd_src)

    if not is_new and os.path.exists("background_state.p"):
        background_state = cPickle.load(open("background_state.p", "rb"))
    else:
        background_state = {"trajectories":[], "params":[], "get_new_parameter":True, "extend_hit":False, "current_user":""}

    if not background_state["trajectories"]:
        prev_trajectories = cPickle.load(open("Trajectories.p","rb"))
        if not os.path.exists("selected_previous_trajectories.p"):
            randomly_picked_users = random.sample(prev_trajectories.keys(), 3)
            cPickle.dump(randomly_picked_users, open("selected_previous_trajectories.p", "wb"))
        else:
            randomly_picked_users = cPickle.load(open("selected_previous_trajectories.p", "rb"))
        for user in randomly_picked_users:
            background_state["trajectories"].append(
                Trajectory(
                    prev_trajectories[user]["pretest"],
                    prev_trajectories[user]["posttest"],
                    prev_trajectories[user]["test_skills"],
                    prev_trajectories[user]["observations"],
                    prev_trajectories[user]["observation_skills"]
                )
            )
        print "Full trajectories added!\n"
        for trajectory in background_state["trajectories"]:
            print toString(trajectory)
        cPickle.dump(background_state, open('background_state.p', 'wb'))

    while True: # continue to create and extend HITs
        # get information about the HIT
        hitid = open("hitid","r").readline()
        assignment_list = mturk_conn.get_assignments(hitid)
        cur_length = len(assignment_list)
        background_state = cPickle.load(open("background_state.p", "rb"))
        if background_state["get_new_parameter"]:
            background_state["params"], temp = next_moe_pts_edu(background_state["trajectories"], edu_expt, rnd_src)
            background_state["get_new_parameter"] = False
            cPickle.dump(background_state, open('background_state.p', 'wb'))
            if cur_length % 10 == 0:
                cPickle.dump(temp, open('best_params{0}'.format(cur_length), 'wb'))

        while True: # wait for the student to start
            assignment_list = mturk_conn.get_assignments(hitid)
            background_state = cPickle.load(open("background_state.p", "rb"))
            if conn.poll():
                received_object = conn.recv()
                if len(received_object) == 1:
                    user_id = received_object[0]
                    params = background_state["params"] # Somehow get the parameters
                    background_state["current_user"] = user_id
                    print "New User {0}!\n".format(user_id)
                    print "With params: {0}\n\n".format(params)
                    conn.send(params)
                    cPickle.dump(params, open('params_' + user_id, 'wb'))
                    cPickle.dump(background_state, open('background_state.p', 'wb'))
                else:
                    received_trajectory = received_object
                    if received_trajectory["user_id"] == background_state["current_user"]:
                        print "User Finished!\n"
                        background_state["extend_hit"] = True
                        new_trajectory = Trajectory(
                            received_trajectory["pretest_scores"],
                            received_trajectory["posttest_scores"],
                            received_trajectory["test2skill"],
                            received_trajectory["trajectory"],
                            received_trajectory["skill_trajectory"]
                        )
                        background_state["trajectories"].append(new_trajectory)
                        background_state["get_new_parameter"] = True
                        cPickle.dump(background_state, open('background_state.p', 'wb'))

            elif len(assignment_list) > cur_length:
                print "User Quit!\n"
                background_state["extend_hit"] = True
                cPickle.dump(background_state, open('background_state.p', 'wb'))

            if background_state["extend_hit"]:
                hit, = mturk_conn.get_hit(hitid, ['HITDetail', 'HITAssignmentSummary'])
                if int(hit.MaxAssignments) == 9: # Need to wait until new HIT is created
                    print "Waiting for new HIT\n"
                    while open("hitid","r").readline() == hitid: # file hitid has to be changed when new HIT is created
                        time.sleep(60)
                elif int(hit.NumberOfAssignmentsPending) + int(hit.NumberOfAssignmentsAvailable) == 0:
                    print "Extended HIT!\n"
                    mturk_conn.extend_hit(hitid, assignments_increment=1)
                    mturk_conn.extend_hit(hitid, expiration_increment=3600 * 5)
                background_state["extend_hit"] = False
                cPickle.dump(background_state, open('background_state.p', 'wb'))
                break

            time.sleep(10)



def toString(trajectory):
    print "{0}\n{1}\n{2}\n{3}\n{4}\n".format(trajectory.pretest, trajectory.posttest,
                                             trajectory.test_skills, trajectory.observs, trajectory.observs_skills)

"""