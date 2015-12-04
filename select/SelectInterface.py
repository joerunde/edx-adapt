class SelectInterface(object):
    """ This is the interface for the adaptive problem
    selection logic. It interacts with the inputted data interface and
    the model interface to pick the next problem to give the user. It does
    not directly store any information about the user or the course.
    """

    def __init__(self, data_interface, model_interface):
        do = "nothing"

    def choose_next_problem(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )
