"""
Use this file or copies of it to control how the Config class generates user profiles

J.L. 11.2020
"""

import random as r
import pandas as pd
import pathlib
from src.NewExperiment.Preferences import search_utility_v_ik

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())


def Psi():
    """
    Determine persuadeability parameter
    Returns: float in [0,1], individuals persuadability
    """
    return 0


def Pi(flag=None):
    """
    Determine political orientation
    Returns pi: political orientation of individual i
    """
    if flag is None or flag == 'political' or flag == 'none':
        return 0
    elif flag == 'left':
        return -1
    elif flag == 'right':
        return 1


def NoiseUtility():
    """
    Returns: epsilon: float, noise parameter when determining utility
    """
    return r.normalvariate(0, 1)


def SelectSearchTerms(pi, alpha_hat, tau_hat_ik):
    """
    Select a subset of all search terms. Terms come from two sepparate pools of terms.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of term lists with keys 'instagram' and 'bigrams' denoting the source of each list.
    """
    path_terms = PRIMEMOVER_PATH + '/resources/input_data/terms.csv'
    terms = pd.read_csv(path_terms, columns=['search_term', 'pi_p'])
    terms['pi_p'] = terms['pi_p'].astype(float)

    utilities = []
    for row in terms.index:
        term_k, pi_hat_k = terms.loc[row]
        # epsilon_ik = NoiseUtility()
        utilities.append((search_utility_v_ik(pi_i=pi,
                                              pi_hat_k=pi_hat_k,
                                              epsilon_ik=0,
                                              alpha_hat=alpha_hat,
                                              tau_hat_ik=tau_hat_ik), term_k,
                          pi_hat_k))
    utilities.sort()
    max_K = utilities[-k:]
    terms = [(b, c) for a, b, c in max_K]
    return terms


def SelectMediaOutlets(pi=0):
    """
    Select a subset of all media outlets.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of outlets with domains as keys and urls as values
    """
    PATH_MEDIA_OUTLETS = PRIMEMOVER_PATH + '/resources/input_data/twitter_stream_top_partisan_domains.csv'
    outlets_twitter = pd.read_csv(PATH_MEDIA_OUTLETS)

    outlets = {}
    if pi == -1:
        outlets_twitter = outlets_twitter.loc[outlets_twitter['party'] == 'D']
    elif pi == 1:
        outlets_twitter = outlets_twitter.loc[outlets_twitter['party'] == 'R']
    else:
        return {}
    index = r.choices(outlets_twitter.index, k=10)
    for i in index:
        outlets[outlets_twitter.loc[i]['domain']] = outlets_twitter.loc[i][
            'url']
    return outlets


def alpha():
    """ Determine alpha, a shift parameter.
    Returns: alpha_hat: float = 0, shift parameter in search term utility
    """
    return 0


def beta():
    """ Determine beta
    Returns: beta: scale parameter in utilities ?
    """
    return r.uniform(0, 1)


def tau():
    """Determine tau tilde, a transportation cost parameter
    Returns: tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    """
    return 1


def kappa():
    """Determine kappa, a persuadability indicator
    Returns: kappa: binary {0,1}, indicates  whether ind. can be persuaded
    """
    return 1


def location():
    return None
