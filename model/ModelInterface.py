class ModelInterface(object):
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

    def get_probability_correct(self, trajectory, parameters):
        raise NotImplementedError( "Data module must implement this" )