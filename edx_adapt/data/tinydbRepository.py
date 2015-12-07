"""Repository that implements DataInterface using a tinydb backend """

import interface
from tinydb import TinyDB, Query


class TinydbRepository(interface.DataInterface):

    def __init__(self, db_path):
        super(TinydbRepository, self).__init__()

        # Create or load backing store
        self.db = TinyDB(db_path)
        self.generic_table_name = "Generic"

        # Create generic key/val store table if it doesn't exist
        if self.generic_table_name not in self.db.tables():
            self.generic = self.db.table("Generic")

        """ Course setup methods """
    def post_course(self, course_id):
        self.assert_no_table(course_id)

        ctable = self.db.table(course_id)
        self.db_set(ctable, 'users_in_progress', [])
        self.db_set(ctable, 'users_finished', [])
        self.db_set(ctable, 'skills', [])
        self.db_set(ctable, 'problems', [])
        self.db_set(ctable, 's2p', {})
        self.db_set(ctable, 'pretest', [])
        self.db_set(ctable, 's2pre', {})
        self.db_set(ctable, 'posttest', [])
        self.db_set(ctable, 's2post', {})

    def post_skill(self, course_id, skill_name):
        self.assert_table(course_id)

        ctable = self.db.table(course_id)
        self.db_append(ctable, 'skills', skill_name)

        s2p = self.db_get(ctable, 's2p')
        s2p[skill_name] = []
        self.db_set(ctable, 's2p', s2p)

    def post_problem(self, course_id, skill_names, problem_name, tutor_url):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        self.append_problem(ctable, 'problems', problem_name, tutor_url)
        self.map_skills(ctable, 's2p', problem_name, skill_names)

    def post_pretest_problem(self, course_id, skill_names, problem_name, tutor_url):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        self.append_problem(ctable, 'pretest', problem_name, tutor_url)
        self.map_skills(ctable, 's2pre', problem_name, skill_names)

    def post_posttest_problem(self, course_id, skill_names, problem_name, tutor_url):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        self.append_problem(ctable, 'posttest', problem_name, tutor_url)
        self.map_skills(ctable, 's2post', problem_name, skill_names)

    def enroll_user(self, course_id, user_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        self.db_append(ctable, 'users_in_progress', user_id)

    """ Retrieve course information """
    def get_course_ids(self):
        courses = self.db.tables()
        courses.remove('_default')
        courses.remove(self.generic_table_name)
        return courses

    def get_skills(self, course_id):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        return self.db_get(ctable, 'skills')

    def get_problems(self, course_id, skill_name):
        self.assert_table(course_id)
        ctable = self.db.table(course_id)
        probs = []
        s2p = self.db_get(ctable, 's2p')
        for pdict in self.db_get(ctable, 'problems'):
            if pdict['problem_name'] in s2p[skill_name]:
                probs.append(pdict)
        # TODO: pretest/posttest flag here...?
        return probs

    def get_num_pretest(self, course_id, skill_name):
        raise NotImplementedError( "Data module must implement this" )

    def get_num_posttest(self, course_id, skill_name):
        raise NotImplementedError( "Data module must implement this" )

    def get_in_progress_users(self, course_id):
        return self.users[course_id]['progress']

    def get_finished_users(self, course_id):
        return self.users[course_id]['finished']


    """ Add user data """
    def post_interaction(self, course_id, problem_name, user_id, correct, attempt, unix_seconds):
        raise NotImplementedError( "Data module must implement this" )

    def post_load(self, course_id, problem_name, user_id, unix_seconds):
        raise NotImplementedError( "Data module must implement this" )

    def set_next_problem(self, course_id, user_id, problem_dict):
        raise NotImplementedError( "Data module must implement this" )

    def advance_problem(self, course_id, user_id):
        """
        required: Must set user's next problem to 'None'
        """
        raise NotImplementedError( "Data module must implement this" )

    """ Retrieve user information """
    def get_all_remaining_problems(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_remaining_problems(self, course_id, skill_name, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_all_remaining_posttest_problems(selfself, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_remaining_posttest_problems(selfself, course_id, skill_name, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_all_interactions(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_interactions(self, course_id, skill_name, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_current_problem(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_next_problem(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_raw_user_data(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_all_raw_data(self, course_id):
        raise NotImplementedError( "Data module must implement this" )



    """ Methods to group users by experiment, e.g. for AB policy testing """
    def post_experiment(self, course_id, experiment_name, start, end):
        raise NotImplementedError( "Data module must implement this" )

    def get_experiments(self, course_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_experiment(self, course_id, experiment_name):
        raise NotImplementedError( "Data module must implement this" )

    def get_subjects(self, course_id, experiment_name):
        raise NotImplementedError( "Data module must implement this" )

    def delete_experiment(self, course_id, experiment_name):
        raise NotImplementedError( "Data module must implement this" )



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
        return result[0]

    def db_append(self, table, listkey, val):
        """@type table: TinyDB"""
        l = self.db_get(table, listkey)
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

    def append_problem(self, ctable, key, problem_name, tutor_url):
        """key can indicate the problem list, pretest list, or posttest list here"""
        self.db_append(ctable, key, {'problem_name': problem_name, 'tutor_url': tutor_url})
        #problems = self.db_get(ctable, key)
        #problems.append({'problem_name': problem_name, 'tutor_url': tutor_url})
        #self.db_set(ctable, key, problems)

    def map_skills(self, ctable, key, problem_name, skill_names):
        """key can indicate the problem, pretest, or posttest mappings here"""
        s2p = self.db_get(ctable, key)
        for skill in skill_names:
            s2p[skill].append(problem_name)
        self.db_set(ctable, key, s2p)