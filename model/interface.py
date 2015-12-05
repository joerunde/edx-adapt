class ModelInterface(object):
    """ This is the interface for the student model that models
    the student mastery of the material. It is a stateless module,
    so it stores no information about the student or the course.
    It gets the trajectory of correctness (0 or 1),
    and a set of parameters as a dictionary, and computes
    the probabilty of getting the next question correct
    """

    def get_probability_correct(self, pretest_score, num_pretest, trajectory, parameters):
        """
        Get the probability of getting the next problem correct according to the student model

        :param pretest_score: number of problems the student got correct on the pre-test
        :param num_pretest: total number of problems on the pre-test
        :param trajectory: trajectory of binary variables indicating whether the student
                           got the problem correct
        :param parameters: dictionary of parameters defining the student model
        :return: the probability of getting the next problem correct
        """
        raise NotImplementedError('Data module must implement this')