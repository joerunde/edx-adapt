"""Repository that implements DataInterface using a tinydb backend """

import datetime
import interface
from tinydb import TinyDB, Query


class TinydbRepository(interface.DataInterface):

    def __init__(self, db_path):
        super(TinydbRepository, self).__init__()

        # Create or load backing store
        self.db = TinyDB(db_path)
        self.generic_table_name = "Generic"
        self.generic = self.db.table(self.generic_table_name)

        """ Course setup methods """
    def post_course(self, course_id):
        self.assert_no_table(course_id)

        ctable = self.db.table(course_id)
        self.db_set(ctable, 'users_in_progress', [])
        self.db_set(ctable, 'users_finished', [])
        self.db_set(ctable, 'skills', [])
        self.db_set(ctable, 'problems', [])
        self.db_set(ctable, 'experiments', [])

    def post_skill(self, course_id, skill_name):
        self.assert_table(course_id)

        ctable = self.db.table(course_id)
        self.db_append(ctable, 'skills', skill_name)

    def _add_problem(self, course_id, skill_names, problem_name, tutor_url, b_pretest, b_posttest):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        skills = self.db_get(ctable, 'skills')
        for skill in skill_names:
            if skill not in skills:
                raise interface.DataException("No such skill: {}".format(skill))
        self.db_append(ctable, 'problems', {'problem_name': problem_name, 'tutor_url': tutor_url,
                                            'pretest': b_pretest, 'posttest': b_posttest, 'skills':skill_names})

    def post_problem(self, course_id, skill_names, problem_name, tutor_url):
        self._add_problem(course_id, skill_names, problem_name, tutor_url, False, False)

    def post_pretest_problem(self, course_id, skill_names, problem_name, tutor_url):
        self._add_problem(course_id, skill_names, problem_name, tutor_url, True, False)

    def post_posttest_problem(self, course_id, skill_names, problem_name, tutor_url):
        self._add_problem(course_id, skill_names, problem_name, tutor_url, False, True)

    def enroll_user(self, course_id, user_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        self.db_append(ctable, 'users_in_progress', user_id)
        self.db_set(ctable, self.get_user_log_key(user_id), [])
        self.db_set(ctable, self.get_user_problem_key(user_id), {'current': None, 'next': None})
        # TODO: have dexter make a choose_first in selector

    """ Retrieve course information """
    def get_course_ids(self):
        courses = self.db.tables()
        courses.remove('_default')
        courses.remove(self.generic_table_name)
        return list(courses)

    def get_skills(self, course_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, 'skills')

    def get_problems(self, course_id, skill_name=None):
        """ Get all problems related to this course-skill pair:, pretest, normal, and posttest """
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        problems = self.db_get(ctable, 'problems')
        if skill_name == None:
            return problems
        else:
            return [x for x in problems if skill_name in x['skills']]

    def get_num_pretest(self, course_id, skill_name):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        pretest = [x for x in self.db_get(ctable, 'problems') if x['pretest'] == True]
        return len(pretest)

    def get_num_posttest(self, course_id, skill_name):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        posttest = [x for x in self.db_get(ctable, 'problems') if x['posttest'] == True]
        return len(posttest)

    def get_in_progress_users(self, course_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, 'users_in_progress')

    def get_finished_users(self, course_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, 'users_finished')

    """ Add user data """
    def post_interaction(self, course_id, problem_name, user_id, correct, attempt, unix_seconds):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        problem = self._get_problem(ctable, problem_name)
        key = self.get_user_log_key(user_id)
        data = {'problem': problem, 'correct': correct, 'attempt': attempt, 'unix_s': unix_seconds, 'type': 'response',
                'timestamp': datetime.datetime.fromtimestamp(unix_seconds).strftime('%Y-%m-%d %H:%M:%S')}
        try:
            self.db_append(ctable, key, data)
        except interface.DataException:
            pass # this just means the interaction already exists, don't need to throw error here

        # is user finished...?
        remaining_post = self.get_all_remaining_posttest_problems(course_id, user_id)
        if len(remaining_post) == 0:
            if user_id in self.get_in_progress_users(course_id):
                self.db_append(ctable, 'users_finished', user_id)
                prog = self.db_get(ctable, 'users_in_progress')
                prog.remove(user_id)
                self.db_set(ctable, 'users_in_progress', prog)

    def post_load(self, course_id, problem_name, user_id, unix_seconds):
        # TODO: maybe only record one load per problem. Think about users exiting and restarting...?
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        problem = self._get_problem(ctable, problem_name)
        key = self.get_user_log_key(user_id)
        data = {'problem': problem, 'unix_s': unix_seconds, 'type': 'page_load',
                'timestamp': datetime.datetime.fromtimestamp(unix_seconds).strftime('%Y-%m-%d %H:%M:%S')}
        try:
            self.db_append(ctable, key, data)
        except interface.DataException:
            pass # this just means the interaction already exists, don't need to throw error here

    def set_next_problem(self, course_id, user_id, problem_dict):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        # if no error, assert that this problem exists in this course:
        if 'error' not in problem_dict:
            problem_dict = self.get_and_assert_problem_exists(ctable, problem_dict)

        curnext = self.db_get(ctable, self.get_user_problem_key(user_id))
        curnext['next'] = problem_dict
        self.db_set(ctable, self.get_user_problem_key(user_id), curnext)

    def advance_problem(self, course_id, user_id):
        """
        required: Must set user's next problem to 'None'
        """
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        curnext = self.db_get(ctable, self.get_user_problem_key(user_id))
        # assert that next problem is valid (it could be an error message)
        next_problem = self.get_and_assert_problem_exists(ctable, curnext['next'])
        curnext['current'] = next_problem
        curnext['next'] = None
        self.db_set(ctable, self.get_user_problem_key(user_id), curnext)

    """ Retrieve user information """
    def get_all_remaining_problems(self, course_id, user_id):
        return [x for x in self._get_remaining_by_user(course_id, user_id)
                if x['pretest'] == False and x['posttest'] == False]

    def get_remaining_problems(self, course_id, skill_name, user_id):
        remaining = self.get_all_remaining_problems(course_id, user_id)
        return [x for x in remaining if skill_name in x['skills']]

    def get_all_remaining_posttest_problems(self, course_id, user_id):
        return [x for x in self._get_remaining_by_user(course_id, user_id) if x['posttest'] == True]

    def get_remaining_posttest_problems(self, course_id, skill_name, user_id):
        remaining = self.get_all_remaining_posttest_problems(course_id, user_id)
        return [x for x in remaining if skill_name in x['skills']]

    def get_all_remaining_pretest_problems(self, course_id, user_id):
        return [x for x in self._get_remaining_by_user(course_id, user_id) if x['pretest'] == True]

    def get_remaining_pretest_problems(self, course_id, skill_name, user_id):
        remaining = self.get_all_remaining_pretest_problems(course_id, user_id)
        return [x for x in remaining if skill_name in x['skills']]

    def get_whole_trajectory(self, course_id, user_id):
        return [x['correct'] for x in self.get_all_interactions(course_id, user_id)]

    def get_skill_trajectory(self, course_id, skill_name, user_id):
        return [x['correct'] for x in self.get_interactions(course_id, skill_name, user_id)]

    def get_all_interactions(self, course_id, user_id):
        return[{'problem': x['problem'], 'correct': x['correct']}
               for x in self.get_raw_user_data(course_id, user_id) if x['type'] == 'response' and x['attempt'] == 1]

    def get_interactions(self, course_id, skill_name, user_id):
        return[{'problem': x['problem'], 'correct': x['correct']}
               for x in self.get_raw_user_skill_data(course_id, skill_name, user_id)
               if x['type'] == 'response' and x['attempt'] == 1]

    def get_current_problem(self, course_id, user_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, self.get_user_problem_key(user_id))['current']

    def get_next_problem(self, course_id, user_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, self.get_user_problem_key(user_id))['next']

    def get_raw_user_data(self, course_id, user_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, self.get_user_log_key(user_id))

    def get_raw_user_skill_data(self, course_id, skill_name, user_id):
        return [x for x in self.get_raw_user_data(course_id, user_id) if skill_name in x['problem']['skills']]


    """ Methods to group users by experiment, e.g. for AB policy testing """
    def post_experiment(self, course_id, experiment_name, start, end):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        experiment = {'experiment_name': experiment_name, 'start_time': start, 'end_time': end}
        self.db_append(ctable, 'experiments', experiment)

    def get_experiments(self, course_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, 'experiments')

    def get_experiment(self, course_id, experiment_name):
        expl = [x for x in self.get_experiments(course_id) if x['experiment_name'] == experiment_name]
        if len(expl) == 0:
            raise interface.DataException("Experiment not found: {}".format(experiment_name))
        return expl[0]

    def get_subjects(self, course_id, experiment_name):
        # return finished users who answered posttest questions within the time frame
        exp = self.get_experiment(course_id, experiment_name)
        users = self.get_finished_users(course_id)
        # not gonna try to put this all in one list comprehension...
        subjects = []
        for user in users:
            data = self.get_raw_user_data(course_id, user)
            for d in data:
                if d['problem']['posttest'] and d['unix_s'] > exp['start_time'] and d['unix_s'] < exp['end_time']:
                    subjects.append(user)
                    continue
        return subjects

    def delete_experiment(self, course_id, experiment_name):
        exp = self.get_experiment(course_id, experiment_name)
        ctable = self.db.table(course_id)
        l = self.db_get(ctable, 'experiments')
        l.remove(exp)
        self.db_set(ctable, 'experiments', l)



    """ General backing store access: allows other modules
    access to persistent storage
    """
    def set(self, key, value):
        self.db_set(self.generic, key, value)
    def get(self, key):
        return self.db_get(self.generic, key)

    def db_set(self, table, key, val):
        """@type table: TinyDB"""
        element = Query()
        table.remove(element.key == key)
        table.insert({'key':key, 'val': val})

    def db_get(self, table, key):
        """@type table: TinyDB"""
        element = Query()
        result = table.search(element.key == key)
        if len(result) == 0:
            raise interface.DataException("Key {} not found in table".format(key))
        return result[0]['val']

    def db_append(self, table, listkey, val):
        """@type table: TinyDB"""
        l = self.db_get(table, listkey)
        if val in l:
            raise interface.DataException("Value: {0} already exists in list: {1}".format(val, listkey))
        l.append(val)
        self.db_set(table, listkey, l)

    def assert_no_table(self, name):
        table = self.db.table(name)
        if len(table) > 0:
            raise interface.DataException("Table already exists: {}".format(name))

    def assert_table(self, name):
        table = self.db.table(name)
        if len(table) == 0:
            raise interface.DataException("Table does not exist: {}".format(name))

    def get_user_log_key(self, user_id):
        return user_id + "_log"

    def get_user_problem_key(self, user_id):
        return user_id + "_cur_next"

    def _get_problem(self, ctable, problem_name):
        problems = self.db_get(ctable, 'problems')
        problem = [x for x in problems if x['problem_name'] == problem_name]
        if len(problem) == 0:
            raise interface.DataException("Problem not found: {}".format(problem_name))
        return problem[0]

    def get_probs_done(self, ctable, user_id):
        log = self.db_get(ctable, self.get_user_log_key(user_id))
        done = []
        for interaction in log:
            if interaction['type'] == 'response':
                if interaction['problem'] not in done:
                    done.append(interaction['problem'])
        return done

    def _get_remaining_by_user(self, course_id, user_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        all = self.db_get(ctable, 'problems')
        done = self.get_probs_done(ctable, user_id)
        remaining = [x for x in all if x not in done]
        return remaining

    def get_and_assert_problem_exists(self, ctable, problem_dict):
        problems = self.db_get(ctable, 'problems')
        if problem_dict not in problems:
            # still try to look up the problem
            if 'problem_name' not in problem_dict:
                raise interface.DataException("Next problem not in database, "
                                              "and does not contain problem_name: {}".format(str(problem_dict)))
            problem_dict = self._get_problem(ctable, problem_dict['problem_name'])
            # above line will raise exception if it can't be found
        return problem_dict
