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

    parameter_access_mode_list = ["course"] # List of the granularity of parameters
                                    # (If per course, "course"; if per skill, "skill"; if per user, "user")
    valid_mode_list = ["course", "user", "skill"]

    def __init__(self, data_interface, model_interface, parameter_access_mode = ""):
        """
        Constructor with the running mode specified, where running mode specifies
        whether the parameters are specified per course, per user, per skill, etc.

        :param data_interface: data module storing state information about the user and the course
        :param model_interface: model interface that computes the probability of getting the next problem correct
        :param parameter_access_mode: Mode that defines the granularity of the parameters
                                      If per skill, "skill"; if per user, "user"
                                      These can be combined. ex) "user skill" - per user and skill
                                      The order must match the order of keys used in data module's set method
                                      For instance, if "user skill", key should be "user_id skill_name"
                                      Note, by default, the parameters are separate per course
                                      So if the string is empty, there is one parameter set per course
        """
        super(SkillSeparateRandomSelector, self).__init__(data_interface, model_interface)

        print self.data_interface
        print self.model_interface
        print self.model_interface.get_probability_correct

        self.parameter_access_mode_list.extend(parameter_access_mode.split())
        for mode in self.parameter_access_mode_list:
            if mode not in self.valid_mode_list:
                raise SelectException("Parameter access mode is invalid")


    def get_p_list(self, namelist, course, user):
        probs = self.data_interface.get_problems(course)
        prob_list = []
        for name in namelist:
            prob_list.extend([x for x in probs if x['problem_name'] == name])

        done = self.data_interface.get_all_interactions(course, user)
        for p in done:
            if p['problem'] in prob_list:
                prob_list.remove(p['problem'])

        new_prob_list = []
        for prob in prob_list:
            skill = prob['skills'][0]
            skill_parameter = self.data_interface.get(self._get_key(course, user, skill))
            prob_mastery = self.model_interface.get_probability_mastered(
                self.data_interface.get_skill_trajectory(course, skill, user), # trajectory of correctness
                skill_parameter # parameters for the skill
            )
            print "threshold",skill_parameter['threshold'],'prob mastery',prob_mastery
            # If the probability is less than threshold, add the problems to candidate list
            if prob_mastery < skill_parameter['threshold']:
                new_prob_list.append(prob)
        return new_prob_list


    def choose_next_problem(self, course_id, user_id):
        """
        Choose the next problem to give to the user

        :param course_id
        :param user_id
        :return: the next problem to give to the user
        """
        try:
            #if pretest problems are left, give the next one
            pretest_problems = self.data_interface.get_all_remaining_pretest_problems(course_id, user_id)
            if len(pretest_problems) > 0:
                for id in range(14):
                    prob = 'Pre_assessment_'+str(id)
                    for pre_prob in pretest_problems:
                        if pre_prob['problem_name'] == prob:
                            return pre_prob
                print "This should never print"
                #return sorted(pretest_problems, key=lambda k: k['problem_name'])[0]

            #Do the first 3 baseline problems (if model says to)
            for prob in self.get_p_list(['b3','b4','b3_2_0'], course_id, user_id):
                return prob
            #Do the next 2 problems always
            p_done = self.data_interface.get_all_interactions(course_id, user_id)
            p_all = self.data_interface.get_problems(course_id)
            for prob in ['labels_we', 'skew_easy_0']:
                give = True
                for p in p_done:
                    if p['problem']['problem_name'] == prob:
                        give = False
                if give:
                    ret = [x for x in p_all if x['problem_name'] == prob]
                    if len(ret) > 0:
                        return ret[0]

            #if the user has started the post-test, finish it
            if len( [x for x in self.data_interface.get_all_interactions(course_id, user_id) if x['problem']['posttest']]) > 0:
                post = self.data_interface.get_all_remaining_posttest_problems(course_id, user_id)
                if len(post) > 0:
                    for id in range(14):
                        prob = 'Post_assessment_'+str(id)
                        for post_prob in post:
                            if post_prob['problem_name'] == prob:
                                return post_prob
                    print "This should never print"

                if len(post) == 0:
                    return {'congratulations': True, 'done': True}
                return post[0]

            candidate_problem_list = [] # List of problems to choose from
            for skill_name in self.data_interface.get_skills(course_id): # For each skill
                if skill_name == 'None':
                    continue
                # Gets the parameters corresponding to the course, user, skill - parameter set must include "threshold"
                skill_parameter = self.data_interface.get(self._get_key(course_id, user_id, skill_name))
                prob_correct = self.model_interface.get_probability_mastered(
                    self.data_interface.get_skill_trajectory(course_id, skill_name, user_id), # trajectory of correctness
                    skill_parameter # parameters for the skill
                )
                # If the probability is less than threshold, add the problems to candidate list
                if prob_correct < skill_parameter['threshold']:
                    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~ " + skill_name + " UNDER THRESHOLD! "
                    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~ adding candidates: " + str(self.data_interface.get_remaining_problems(course_id, skill_name, user_id))
                    candidate_problem_list.extend(self.data_interface.get_remaining_problems(course_id, skill_name, user_id))

            if candidate_problem_list: # If candidate list is not empty, randomly choose one from it
                return random.choice(candidate_problem_list)
            else: # IF candidate list is empty, return post-test
                return self.data_interface.get_all_remaining_posttest_problems(course_id, user_id)[0]

        except DataException as e:
            raise SelectException("DataException: " + e.message)
        except ModelException as e:
            raise SelectException("ModelException: " + e.message)
        except SelectException as e:
            raise e


    def choose_first_problem(self, course_id, user_id):
        """
        Choose the first problem to give to the user

        :param course_id
        :param user_id
        :return: the first problem to give to the user
        """
        pretest = self.data_interface.get_all_remaining_pretest_problems(course_id, user_id)
        for prob in pretest:
            if prob['problem_name'] == 'Pre_assessment_0':
                return prob
        #return sorted(pretest, key=lambda k: k['problem_name'])[0]


    def _get_key(self, course_id, user_id, skill_name):
        """
        Gets the valid key to access the parameters for the specified course, user, skill
        based on the mode specified in the constructor

        :param course_id
        :param user_id
        :param skill_id
        :return: key to access the parameters in the data module
        """
        mode_id_map = {"course": course_id, "user": user_id, "skill": skill_name}
        key = ""
        for mode in self.parameter_access_mode_list:
            if mode in mode_id_map:
                key += str(mode_id_map[mode])
            else:
                raise SelectException("Parameter access mode is invalid")
        return key.strip()


    def get_parameter(self, course_id, user_id = None, skill_name = None):
        mode_id_map = {"course": course_id, "user": user_id, "skill": skill_name}

        key = ""
        for mode in self.parameter_access_mode_list:
            if mode_id_map[mode]:
                key += mode_id_map[mode]
            else:
                raise SelectException("Mode and the arguments do not match")
        return self.data_interface.get(key)

    def set_parameter(self, parameter, course_id = None, user_id = None, skill_name = None):
        """
        Set the parameter for the specified course, user, skill (all optional)

        :param parameter: dictionary containing the set of parameters
        :param course_id
        :param user_id
        :param skill_name
        """
        mode_id_map = {"course": course_id, "user": user_id, "skill": skill_name}

        key = ""
        for mode in self.parameter_access_mode_list:
            if mode_id_map[mode]:
                key += mode_id_map[mode]
            else:
                raise SelectException("Mode and the arguments do not match")
        self.data_interface.set(key, parameter)