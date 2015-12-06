import random

from interface import SelectInterface, SelectException
from data.interface import DataException
from model.interface import ModelException

class SkillSeparateRandomSelector(SelectInterface):

    def choose_next_problem(self, course_id, user_id):
        try:
            candidate_problem_list = []
            for skill_name in self.data_interface.get_skills(course_id):
                skill_parameter = self.data_interface.get(skill_name)
                prob_correct = self.model_interface.get_probability_correct(
                    self.data_interface.get_num_pretest(course_id, skill_name), # number of pre-test problems on the skill
                    self.data_interface.get_interactions(course_id, skill_name, user_id), # trajectory of correctness
                    skill_parameter # parameters for the skill
                )
                # If the probability is less than threshold, add the problems to canself.data_interfacedate list
                if prob_correct < skill_parameter['threshold']:
                    candidate_problem_list.append(self.data_interface.get_remaining_problems(course_id, skill_name, user_id))

            if candidate_problem_list:
                return random.choice(candidate_problem_list)
            else:
                return self.data_interface.get_all_remaining_posttest_problems(course_id, user_id)[0]

        except DataException as e:
            raise SelectException("DataException: " + e.message)
        except ModelException as e:
            raise SelectException("ModelException: " + e.message)
