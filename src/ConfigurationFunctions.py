"""
Use this file or copies of it to control how the Config class generates user profiles

J.L. 11.2020
"""

import random as r
import pandas as pd
from numpy.random import gumbel
import pathlib
from src.Preferences import search_utility_v_ik, media_utility_u_ij

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())


def Psi():
    """
    Determine persuadeability parameter
    Returns: float in [0,1], individuals persuadability
    """
    return r.uniform(0, 0.2)


def Pi(flag=None):
    """
    Determine political orientation
    Returns pi: political orientation of individual i
    """
    if flag == 'left':
        pi = r.uniform(-1, 0)
    elif flag == 'right':
        pi = r.uniform(0, 1)
    else:
        pi = r.uniform(-1, 1)
    return pi


def NoiseUtility():
    """
    Returns: epsilon: float, noise parameter when determining utility
    """
    return float(gumbel(-0.4557735, 0.793006, 1)[0]) / 10


def SelectSearchTerms(pi, alpha_hat, tau_hat_ik, k=40):
    """
    Select a subset of all search terms. Terms come from two sepparate pools of terms.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of term lists with keys 'instagram' and 'bigrams' denoting the source of each list.
    """
    path_terms = PRIMEMOVER_PATH + '/resources/input_data/searchterms_pool.csv'
    terms = pd.read_csv(path_terms, usecols=['search_term', 'pi_p'])
    terms['pi_p'] = terms['pi_p'].astype(float)

    utilities = []
    for row in terms.index:
        term_k, pi_hat_k = terms.loc[row]
        epsilon_ik = NoiseUtility()
        utilities.append((search_utility_v_ik(pi_i=pi,
                                              pi_hat_k=pi_hat_k,
                                              epsilon_ik=epsilon_ik,
                                              alpha_hat=alpha_hat,
                                              tau_hat_ik=tau_hat_ik), term_k,
                          pi_hat_k))
    utilities.sort()
    max_K = utilities[-k:]
    terms = [{'term': b, 'pi': c} for a, b, c in max_K]
    return terms


def SelectMediaOutlets(alpha_tilde, tau_tilde_ij, state, pi=0, k=10):
    """
    Select a subset of all media outlets.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of outlets with domains as keys and urls as values
    """
    us_pop = 327533774

    path_outlets = PRIMEMOVER_PATH + '/resources/input_data/outlets_pool.csv'
    outlets = pd.read_csv(path_outlets,
                          usecols=['domain', 'pub_state', 'redirect_url',
                                   'avg_users_us_percent',
                                   'avg_reach_permillion', 'pi', 'pop2019',
                                   'is_local'])
    outlets['pi'] = outlets['pi'].astype(float)
    outlets['avg_users_us_percent'] = outlets['avg_users_us_percent'].astype(
        float)
    outlets['avg_reach_permillion'] = outlets['avg_reach_permillion'].astype(
        float)
    outlets['pop2019'] = outlets['pop2019'].astype(
        float)
    outlets['is_local'] = outlets['is_local'].astype(
        bool)

    weighted_utilities = []
    for row in outlets.index:
        epsilon_ij = NoiseUtility()
        s_j = outlets.loc[row]['pub_state']
        if outlets.loc[row]['is_local'] and (type(s_j) is str):
            if state in s_j:
                weight = outlets.loc[row]['avg_reach_permillion'] * \
                         outlets.loc[row]['avg_users_us_percent'] * us_pop / \
                         outlets.loc[row]['pop2019']
            else:
                weight = 0
        else:
            weight = outlets.loc[row]['avg_reach_permillion'] * \
                     outlets.loc[row]['avg_users_us_percent'] / 100
        weighted_utilities.append(((weight * media_utility_u_ij(pi_i=pi,
                                                                pi_tilde_j=
                                                                outlets.loc[
                                                                    row]['pi'],
                                                                epsilon_ij=epsilon_ij,
                                                                alpha_tilde=alpha_tilde,
                                                                tau_tilde_ij=tau_tilde_ij),
                                    outlets.loc[row]['domain'],
                                    outlets.loc[row]['redirect_url'],
                                    outlets.loc[row]['pi'])))
    weighted_utilities.sort()
    max_K = weighted_utilities[-k:]
    outlets = [{'domain': domain, 'url': url, 'pi': pi} for
               util, domain, url, pi in max_K]
    return outlets


def update_media_outlets(outlets, pi, alpha_tilde, tau_tilde_ij, k=10):
    utilities = []
    for outlet in outlets:
        epsilon_ij = NoiseUtility()
        utilities.append(((media_utility_u_ij(pi_i=pi,
                                              pi_tilde_j=outlet['pi'],
                                              epsilon_ij=epsilon_ij,
                                              alpha_tilde=alpha_tilde,
                                              tau_tilde_ij=tau_tilde_ij),
                           outlet['domain'],
                           outlet['url'],
                           outlet['pi'])))
    utilities.sort()
    max_K = utilities[-k:]
    outlets = [{'domain': domain, 'url': url, 'pi': pi} for
               util, domain, url, pi in max_K]
    return outlets


def alpha():
    """ Determine alpha, a shift parameter.
    Returns: alpha_hat: float = 0, shift parameter in search term utility
    """
    return r.uniform(0.2, 0.5)


def beta():
    """ Determine beta
    Returns: beta: scale parameter in utilities ?
    """
    return r.uniform(0, 0.5)


def tau():
    """Determine tau tilde, a transportation cost parameter
    Returns: tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    """
    return 1


def kappa():
    """Determine kappa, a persuadability indicator
    Returns: kappa: binary {0,1,2}, indicates  whether ind. can be persuaded
    """
    return r.choices([0, 1, 2], [0.25, 0.25, 0.5])[0]


def location():
    return "US-AL-AUBURN"


def usage_type():
    choice = \
    r.choices(['only_search', 'only_direct', 'both'], [0.25, 0.25, 0.5])[0]
    return choice


def cookie_pref():
    pref = {'accept_all': True}
    if not pref['accept_all']:
        pref['SearchCustom'] = r.choice([True, False])
        pref['YoutubeHist'] = r.choice([True, False])
        pref['AdCustom'] = r.choice([True, False, 'More'])
        if pref['AdCustom'] == 'More':
            pref['GoogleAds'] = False
            pref['YoutubeAds'] = False
    return pref

"""
Profile configuration functions
"""


def language():
    """
    Randomly assign US-English
        ("en-US,en;q=0.5")1 as the language setting to 3/4 of
        the bots and
        (latin-american) Spanish, with American-English as alternative
        ("es-MX,es;q=0.8,en-US;q=0.5,en;q=0.3")
    returns: One of the two language strings above
    """
    languages = ["en-US,en;q=0.5", "es-MX,es;q=0.8,en-US;q=0.5,en;q=0.3"]
    choice = r.choices(languages, [0.75, 0.25])[0]
    return choice


def geolocation(option_choice='random'):
    if option_choice == 'random':
        choice = r.choices(['BLOCK', 'ALLOW'], [0.2, 0.8])[0]
    elif option_choice == 'geolocation':
        choice = 'BLOCK'
    else:
        choice = 'ALLOW'
    return choice


def do_not_track(option_choice='random'):
    if option_choice == 'random':
        choice = r.choices([0, 1], [0.8, 0.2])[0]
    elif option_choice == 'do_not_track':
        choice = 1
    else:
        choice = 0
    return choice


def hardware_canvas(option_choice='random'):
    if option_choice == 'random':
        choice = r.choices(['BLOCK', 'NOISE'], [0.2, 0.8])[0]
    elif option_choice == 'hardware_canvas':
        choice = 'BLOCK'
    else:
        choice = 'NOISE'
    return choice


def local_storage(option_choice='random'):
    if option_choice == 'random':
        choice = r.choices([True, False], [0.8, 0.2])[0]
    elif option_choice == 'local_storage':
        choice = False
    else:
        choice = True
    return choice


if __name__ == "__main__":
    a = SelectMediaOutlets(15, 1, 1, 'US-CA')
    print(a)
    b = SelectSearchTerms(0, 1, 0, 10)
    print(b)
