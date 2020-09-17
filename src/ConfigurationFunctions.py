import random as r
from src.Preferences import *
import json

"""
Use this file or copies of it to control how the Config class generates user profiles
"""

with open("resources/other/geosurf_cities.json", 'r') as file:
    LOCATION_LIST = list(json.load(file).keys())


def Psi():
    """
    :return: float in [0,1], individuals persuadability
    """
    return r.normalvariate(0, 1)


def Pi():
    """
    :return pi: political orientation of individual i
    """
    return r.normalvariate(0, 1)


def NoiseUtility():
    """
    :return epsilon: float, noise parameter when determining utility
    """
    return r.normalvariate(0, 1)


def SelectSearchTerms(pi_i, term_pi_tbl, n):
    # utilities = {}
    # for term_k, pi_hat_k in term_pi_tbl:
    #     epsilon_ik = NoiseUtility()
    #     utilities['term'] = search_utility_v_ik(pi_i=pi_i,
    #                                             pi_hat_k=pi_hat_k,
    #                                             epsilon_ik=epsilon_ik,
    #                                             alpha_hat=0,
    #                                             tau_hat_ik=1)
    return random.sample(term_pi_tbl['search_term'].to_list(), n)


def SelectMediaOutlets(url_pi_tbl=None, n=1000, pi_i=0):
    # utilities = {}
    # for term_k, pi_hat_k in term_pi_tbl:
    #     epsilon_ik = NoiseUtility()
    #     utilities['term'] = search_utility_v_ik(pi_i=pi_i,
    #                                             pi_hat_k=pi_hat_k,
    #                                             epsilon_ik=epsilon_ik,
    #                                             alpha_hat=0,
    #                                             tau_hat_ik=1)
    return random.sample(url_pi_tbl['url'].to_list(), n)


def alpha():
    """
    :return alpha_hat: float >= 0, shift parameter in search term utility
    """
    return 0


def beta():
    """
    :return beta: scale parameter in utilities ?
    """
    return 1


def tau():
    """
    :return tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    """
    return 1


def kappa():
    """
    :return kappa: binary {0,1}, indicates  whether ind. can be persuaded
    """
    return 0


def location():
    return random.choice(LOCATION_LIST)
