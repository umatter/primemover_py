import random as r
from src.Preferences import *
import json

"""
Use this file or copies of it to control how the Config class generates user profiles
"""

with open("resources/other/testrun_10Oct2020_hometowns.json", 'r') as file:
    LOCATION_LIST = json.load(file)

# with open("resources/other/geosurf_cities.json", 'r') as file:
#     LOCATION_LIST = list(json.load(file).keys())

def Psi():
    """
    :return: float in [0,1], individuals persuadability
    """
    return r.normalvariate(0, 1)


def Pi(flag=None):
    """
    :return pi: political orientation of individual i
    """
    if flag is None or flag == 'political' or flag == 'none':
        return r.uniform(-1, 1)
    elif flag == 'left':
        return r.uniform(-1, 0)
    elif flag == 'right':
        return r.uniform(0, 1)


def NoiseUtility():
    """
    :return epsilon: float, noise parameter when determining utility
    """
    return r.normalvariate(0, 1)


def SelectSearchTerms(pi_i, term_pi_tbl, k, alpha_hat, tau_hat_ik):
    utilities = []
    for row in range(len(term_pi_tbl)):
        term_k, pi_hat_k = term_pi_tbl.loc[row]
        epsilon_ik = NoiseUtility()
        utilities.append((search_utility_v_ik(pi_i=pi_i,
                                              pi_hat_k=pi_hat_k,
                                              epsilon_ik=epsilon_ik,
                                              alpha_hat=alpha_hat,
                                              tau_hat_ik=tau_hat_ik), term_k,
                          pi_hat_k))
    utilities.sort()
    max_K = utilities[-k:]
    terms = [(b, c) for a, b, c in max_K]
    #  random.sample(term_pi_tbl['search_term'].to_list(), k)
    return terms


def SelectMediaOutlets(url_pi_tbl=None, alpha_tilde=0, k=10, tau_tilde_ij=1, pi_i=0):
    # Base on pi, K known outlets,
    utilities = []
    for row in range(len(url_pi_tbl)):
        outlet, exp_rho, pi_tilde_j = url_pi_tbl.loc[row]
        epsilon_ik = NoiseUtility()
        rho = math.log(exp_rho)
        utilities.append(((media_utility_u_ij(pi_i=pi_i,
                                              pi_tilde_j=pi_tilde_j,
                                              epsilon_ij=epsilon_ik,
                                              alpha_tilde=alpha_tilde,
                                              rho_j=rho,
                                              tau_tilde_ij=tau_tilde_ij)),
                          outlet, pi_tilde_j, rho))
    utilities.sort()
    max_K = utilities[-k:]
    outlets = [(url, pi, rho) for util, url, pi, rho in max_K]
    return outlets


def alpha():
    """
    :return alpha_hat: float >= 0, shift parameter in search term utility
    """
    return 0


def beta():
    """
    :return beta: scale parameter in utilities ?
    """
    return random.uniform(0, 1)


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
    return 1


def location():
    LOCATION_LIST = ["US-OK-OKLAHOMA_CITY", "US-CA-SAN_FRANCISCO",
                     "US-NY-NEW_YORK", "US-MA-BOSTON"]
    return random.choice(LOCATION_LIST)
