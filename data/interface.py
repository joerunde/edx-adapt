class DataInterface(object):
    """ This is the interface for the persistent data store
    backing an edX-adapt course. It stores information about
    courses, such as which skills they teach and which problems
    are associated with those skills. It also stores user data,
    such as which users are currently progressing through a
    course, which users have finished the course, and logs of
    the students' interactions with the problems.
    """

    def __init__(self):
        do = "nothing"

    """ Course setup methods """
    def post_course(self, course_id):
        raise NotImplementedError( "Data module must implement this" )

    def post_skill(self, course_id, skill_name):
        raise NotImplementedError( "Data module must implement this" )

    def post_problem(self, course_id, skill_names, problem_name, tutor_url):
        raise NotImplementedError( "Data module must implement this" )

    def post_pretest_problem(self, course_id, skill_names, problem_name, tutor_url):
        raise NotImplementedError( "Data module must implement this" )

    def post_posttest_problem(self, course_id, skill_names, problem_name, tutor_url):
        raise NotImplementedError( "Data module must implement this" )

    def enroll_user(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )

    """ Retrieve course information """
    def get_course_ids(self):
        raise NotImplementedError( "Data module must implement this" )

    def get_skills(self, course_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_problems(self, course_id, skill_name):
        raise NotImplementedError( "Data module must implement this" )

    def get_num_pretest(self, course_id, skill_name):
        raise NotImplementedError( "Data module must implement this" )

    def get_num_posttest(self, course_id, skill_name):
        raise NotImplementedError( "Data module must implement this" )

    def get_in_progress_users(self, course_id):
        raise NotImplementedError( "Data module must implement this" )

    def get_finished_users(self, course_id):
        raise NotImplementedError( "Data module must implement this" )


    """ Add user data """
    def post_interaction(self, course_id, problem_name, user_id, correct, attempt, unix_seconds):
        raise NotImplementedError( "Data module must implement this" )

    def post_load(self, course_id, problem_name, user_id, unix_seconds):
        raise NotImplementedError( "Data module must implement this" )

    def set_next_problem(self, course_id, user_id, problem_name):
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




class DataException(Exception):
    pass
