import math
from interface import ModelInterface

class PFM(ModelInterface):
    """ This is an example implementation of a student model interface.
    Performance Factor Model uses logistic regression to model
    the students, where the sigmoid function is used on the
    number of questions the student got correct until now
    and the number of questions the student got wrong until now
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
        counts = [num_pretest - pretest_score, pretest_score]
        for correctness in trajectory:
            counts[correctness] += 1
        return get_probability(counts, parameters)


def get_probability(counts, params):
    """
    Computes the probability of getting the next problem correct

    :param counts: number of problems the student got incorrect and correct
    :param params: dictionary of parameters containing pi, pt, pg, ps
    :return: probability of getting the next problem correct
    """
    return 1.0 / (1 + math.exp(-(params['beta_intercept'] + params['beta_incorrect'] * counts[0] + params['beta_correct'] * counts[1])))
