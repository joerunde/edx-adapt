""" Mock-up data repository for development/testing
"""

import interface

class MockRepository(interface.DataInterface):

    def __init__(self):
        super(MockRepository, self).__init__()
        self.courses = []
        self.users = {}
        self.skills = {}
        self.problems = {}
        self.p2s = {}
        self.s2p = {}

    """ Course setup methods """
    def post_course(self, course_id):
        self.courses.append(course_id)
        self.users[course_id] = {'progress': [], 'finished': []}
        self.skills[course_id] = []
        self.problems[course_id] = []
        self.p2s[course_id] = {}
        self.s2p[course_id] = {}

    def post_skill(self, course_id, skill_name):
        self.skills[course_id].append(skill_name)
        self.s2p[course_id][skill_name] = []
        raise NotImplementedError( "Data module must implement this" )

    def post_problem(self, course_id, skill_names, problem_name, tutor_url):
        self.problems[course_id].append({'problem_name': problem_name, 'tutor_url': tutor_url})
        self.p2s[course_id][problem_name] = skill_names
        for skill in skill_names:
            self.s2p[course_id][skill].append(problem_name)

    def post_pretest_problem(self, course_id, skill_names, problem_name, tutor_url):
        raise NotImplementedError( "Data module must implement this" )

    def post_posttest_problem(self, course_id, skill_names, problem_name, tutor_url):
        raise NotImplementedError( "Data module must implement this" )

    def enroll_user(self, course_id, user_id):
        self.users[course_id]['progress'].append(user_id)

    """ Retrieve course information """
    def get_course_ids(self):
        return self.courses

    def get_skills(self, course_id):
        return self.skills[course_id]

    def get_problems(self, course_id, skill_name):
        probs = []
        for pdict in self.problems:
            if pdict['problem_name'] in self.s2p[course_id][skill_name]:
                probs.append(pdict)
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
        raise NotImplementedError( "Data module must implement this" )
    def get(self, key):
        raise NotImplementedError( "Data module must implement this" )

