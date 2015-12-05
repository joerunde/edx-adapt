import math
from interface import ModelInterface

class BKT(ModelInterface):
    """ This is an example implementation of a student model interface.
    Bayesian Knowledge Tracing uses a hidden Markov model to model
    the students, where the forward algorithm is used to compute
    the probability of getting the next problem correct
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
        alpha = initialize_probability(parameters, pretest_score, num_pretest)
        for correctness in trajectory:
            update_probability(alpha, parameters, correctness)
        return get_probability_correct(alpha, parameters)

def initialize_probability(params, pretest_score, num_pretest):
    """
    Initialize the forward probability vector according to the pre-test score
    Uses the Bayes rule to compute the probability of knowing or not knowing the knowledge component
    based on the initial probability parameter and the pre-test score

    :param params: dictionary of parameters containing pi, pt, pg, ps
    :param pretest_score: number of problems the student got correct on the pre-test
    :param num_pretest: total number of problems on the pre-test
    :return: initialized forward probability vector
    """
    alpha = [0, 0]
    alpha[0] = (1 - params['pi']) * math.pow(1 - params['pg'], num_pretest - pretest_score) * math.pow(params['pg'], num_pretest)
    alpha[1] = params['pi'] * math.pow(params['ps'], num_pretest - pretest_score) * math.pow(1 - params['ps'], num_pretest)
    norm = alpha[0] + alpha[1]
    alpha[0] /= norm
    alpha[1] /= norm
    return alpha


def update_probability(alpha, params, is_correct):
    """
    Updates the forward probability vector at each time point according to whether
    the student got the problem correct or not

    :param alpha: forward probability vector compiled until this time point
    :param params: dictionary of parameters containing pi, pt, pg, ps
    :param is_correct: whether the student got the last problem correct or not (1-correct, 0-incorrect)
    :return: nothing
    """
    alpha[0] *= params['pg'] * is_correct + (1 - params['pg']) * (1 - is_correct)
    alpha[1] *= (1 - params['ps']) * is_correct + params['ps'] * (1 - is_correct)
    new_alpha = [alpha[0] * (1 - params['pt']), alpha[0] * params['pt'] + alpha[1]]
    alpha[0] = new_alpha[0]
    alpha[1] = new_alpha[1]


def get_probability_correct(alpha, params):
    """
    Computes the probability of getting the next problem correct

    :param alpha: forward probability vector compiled until this time point
    :param params: dictionary of parameters containing pi, pt, pg, ps
    :return: probability of getting the next problem correct
    """
    return (alpha[0] * params['pg'] + alpha[1] * (1 - params['ps'])) / (alpha[0] + alpha[1])
