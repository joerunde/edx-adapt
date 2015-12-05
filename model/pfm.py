import math
from interface import ModelInterface

class PFM(ModelInterface):
    """ This is an example implementation of a student model interface.
    Performance Factor Model uses logistic regression to model
    the students, where the sigmoid function is used on the
    number of questions the student got correct until now
    and the number of questions the student got wrong until now
    """

    counts = [0, 0] # Number of problems the student got incorrect and correct respectively

    def get_probability_correct(self, num_pretest, trajectory, parameters):
        """
        Get the probability of getting the next problem correct according to the student model

        :param num_pretest: number of pre-test problems in this trajectory
        :param trajectory: trajectory of binary variables indicating whether the student
                           got the problem correct
        :param parameters: dictionary of parameters defining the student model
        :return: the probability of getting the next problem correct
        """
        for correctness in trajectory:
            self.counts[correctness] += 1
        return self.get_current_probability_correct(parameters)


    def get_current_probability_correct(self, params):
        """
        Computes the probability of getting the next problem correct

        :param counts: number of problems the student got incorrect and correct
        :param params: dictionary of parameters containing pi, pt, pg, ps
        :return: probability of getting the next problem correct
        """
        return 1.0 / (1 + math.exp(-(params['beta_intercept'] + params['beta_incorrect'] * self.counts[0] + params['beta_correct'] * self.counts[1])))
