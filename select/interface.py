from data.interface import DataInterface
from model.interface import ModelInterface

class SelectInterface(object):
    """ This is the interface for the adaptive problem
    selection logic. It interacts with the inputted data interface and
    the model interface to pick the next problem to give the user. It does
    not directly store any information about the user or the course.
    """

    data_interface = None # Data module which gets the state information
    model_interface = None # Student model

    def __init__(self, data_interface, model_interface):
        self.data_interface = data_interface
        self.model_interface = model_interface

    def choose_next_problem(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )


class SelectException(Exception):
    pass