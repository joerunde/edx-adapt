import SelectInterface

class ProblemSelector(SelectInterface):

    def choose_next_problem(self, course_id, user_id):
        raise NotImplementedError( "Data module must implement this" )