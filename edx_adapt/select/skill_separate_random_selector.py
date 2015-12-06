import random

from interface import SelectInterface, SelectException
from edx_adapt.data.interface import DataException
from edx_adapt.model.interface import ModelException

class SkillSeparateRandomSelector(SelectInterface):
    """ This is an implementation of the adaptive problem selector.
    At each time point, to goes through every skill (can be 1 skill)
    and computes the probability of getting the next problem correct.
    If the probability is less than the threshold parameter, the
    remaining problems corresponding to the skill is added to the
    candidate list, and the next problem is selected randomly from
    the candidate list with the same probability.
    """

    def choose_next_problem(self, course_id, user_id):
        """
        Choose the next problem to give to the user

        :param course_id
        :param user_id
        :return: the next problem to give to the user
        """
        try:
            candidate_problem_list = [] # List of problems to choose from
            for skill_name in self.data_interface.get_skills(course_id): # For each skill
                skill_parameter = self.data_interface.get(skill_name) # Parameter must include "threshold"
                prob_correct = self.model_interface.get_probability_correct(
                    self.data_interface.get_num_pretest(course_id, skill_name), # number of pre-test problems on the skill
                    self.data_interface.get_interactions(course_id, skill_name, user_id), # trajectory of correctness
                    skill_parameter # parameters for the skill
                )
                # If the probability is less than threshold, add the problems to candidate list
                if prob_correct < skill_parameter['threshold']:
                    candidate_problem_list.append(self.data_interface.get_remaining_problems(course_id, skill_name, user_id))

            if candidate_problem_list: # If candidate list is not empty, randomly choose one from it
                return random.choice(candidate_problem_list)
            else: # IF candidate list is empty, return post-test
                return self.data_interface.get_all_remaining_posttest_problems(course_id, user_id)[0]

        except DataException as e:
            raise SelectException("DataException: " + e.message)
        except ModelException as e:
            raise SelectException("ModelException: " + e.message)
