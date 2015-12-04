class SelectInterface(object):
    """ This is the interface for the persistent data store
    backing an edX-adapt course. It stores information about
    courses, such as which skills they teach and which problems
    are associated with those skills. It also stores user data,
    such as which users are currently progressing through a
    course, which users have finished the course, and logs of
    the students' interactions with the problems.
    """

    def __init__(self, data_interface, model_interface):
        do = "nothing"

    def choose_next_problem(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )
