class ModelInterface(object):
    """ This is the interface for the student model that models
    the student mastery of the material. It is a stateless module,
    so it stores no information about the student or the course.
    It gets the trajectory of correctness (0 or 1),
    and a set of parameters as a dictionary, and computes
    the probabilty of getting the next question correct
    """

    def __init__(self):
        do = "nothing"

    def get_probability_correct(self, trajectory, parameters):
        raise NotImplementedError( "Data module must implement this" )