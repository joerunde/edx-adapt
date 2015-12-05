import math
from interface import ModelInterface

class BKT(ModelInterface):
    """ This is an example implementation of a student model interface.
    Bayesian Knowledge Tracing uses a hidden Markov model to model
    the students, where the forward algorithm is used to compute
    the probability of getting the next problem correct
    """

    alpha = [0, 0] # Forward probability vector

    def get_probability_correct(self, num_pretest, trajectory, parameters):
        """
        Get the probability of getting the next problem correct according to the student model

        :param num_pretest: number of pre-test problems in this trajectory
        :param trajectory: trajectory of binary variables indicating whether the student
                           got the problem correct
        :param parameters: dictionary of parameters defining the student model
        :return: the probability of getting the next problem correct
        """
        pretest_score = 0
        for i in xrange(num_pretest):
            pretest_score += trajectory[i]

        self.initialize_probability(parameters, pretest_score, num_pretest)
        for i in xrange(num_pretest + 1, len(trajectory)):
            self.update_probability(parameters, trajectory[i])
        return self.get_current_probability_correct(parameters)

    def initialize_probability(self, params, pretest_score, num_pretest):
        """
        Initialize the forward probability vector according to the pre-test score
        Uses the Bayes rule to compute the probability of knowing or not knowing the knowledge component
        based on the initial probability parameter and the pre-test score

        :param params: dictionary of parameters containing pi, pt, pg, ps
        :param pretest_score: number of problems the student got correct on the pre-test
        :param num_pretest: total number of problems on the pre-test
        """
        self.alpha[0] = (1 - params['pi']) * math.pow(1 - params['pg'], num_pretest - pretest_score) * math.pow(params['pg'], num_pretest)
        self.alpha[1] = params['pi'] * math.pow(params['ps'], num_pretest - pretest_score) * math.pow(1 - params['ps'], num_pretest)
        norm = self.alpha[0] + self.alpha[1]
        self.alpha[0] /= norm
        self.alpha[1] /= norm


    def update_probability(self, params, is_correct):
        """
        Updates the forward probability vector at each time point according to whether
        the student got the problem correct or not

        :param self.alpha: forward probability vector compiled until this time point
        :param params: dictionary of parameters containing pi, pt, pg, ps
        :param is_correct: whether the student got the last problem correct or not (1-correct, 0-incorrect)
        """
        self.alpha[0] *= params['pg'] * is_correct + (1 - params['pg']) * (1 - is_correct)
        self.alpha[1] *= (1 - params['ps']) * is_correct + params['ps'] * (1 - is_correct)
        new_self.alpha = [self.alpha[0] * (1 - params['pt']), self.alpha[0] * params['pt'] + self.alpha[1]]
        self.alpha[0] = new_self.alpha[0]
        self.alpha[1] = new_self.alpha[1]


    def get_current_probability_correct(self, params):
        """
        Computes the probability of getting the next problem correct

        :param self.alpha: forward probability vector compiled until this time point
        :param params: dictionary of parameters containing pi, pt, pg, ps
        :return: probability of getting the next problem correct
        """
        return (self.alpha[0] * params['pg'] + self.alpha[1] * (1 - params['ps'])) / (self.alpha[0] + self.alpha[1])
