class SelectInterface(object):
    """ This is the interface for the adaptive problem
    selection logic. It interacts with the inputted data interface and
    the model interface to pick the next problem to give the user. It does
    not directly store any information about the user or the course.
    """

    data_interface = None # Data module which gets the state information
    model_interface = None # Student model

    def __init__(self, data_interface, model_interface):
        """
        Constructor for the select interface

        :param data_interface: data module storing state information about the user and the course
        :param model_interface: model interface that computes the probability of getting the next problem correct
        """
        self.data_interface = data_interface
        self.model_interface = model_interface

    def choose_next_problem(self, course_id, user_id):
        """
        Choose the next problem to give to the user

        :param course_id
        :param user_id
        :return: the next problem to give to the user
        """
        raise NotImplementedError( "Data module must implement this" )


    def choose_first_problem(self, course_id, user_id):
        """
        Choose the first problem to give to the user

        :param course_id
        :param user_id
        :return: the first problem to give to the user
        """
        raise NotImplementedError( "Data module must implement this" )


    def set_parameter(self, parameter, course_id = None, user_id = None, skill_name = None):
        """
        Set the parameter for the specified course, user, skill (all optional)

        :param parameter: dictionary containing the set of parameters
        :param course_id
        :param user_id
        :param skill_name
        """
        raise NotImplementedError( "Data module must implement this" )


class SelectException(Exception):
    pass