import random as r
from src.Preferences import *


def Psi():
    return r.normalvariate(0,1)


def Pi():
    return r.normalvariate(0,1)


def NoiseUtility():
    return r.normalvariate(0,1)


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




