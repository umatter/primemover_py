"""
Use this file or copies of it to control how the CONFIGURATION_FUNCTIONS class generates user profiles.
The intent is to create an experiment specific copy and replace parameter defining rules.
J.L. 11.2020
"""

import random as r
from numpy.random import gumbel
import pathlib

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


def SelectSearchTerms():
    """
    Select a subset of all search terms. Terms come from two sepparate pools of terms.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of term lists with keys 'instagram' and 'bigrams' denoting the source of each list.
    """
    terms = []
    return terms


def SelectMediaOutlets():
    """
    Select a subset of all media outlets.
    Arguments:
        - pi: political orientation of individual
        - k: nr national outlets
        - local: nr local outlets
    Returns: dictionary of outlets with domains as keys and urls as values
    """
    outlets = []
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
    # languages = ["en-US,en;q=0.5", "es-MX,es;q=0.8,en-US;q=0.5,en;q=0.3"]
    # choice = r.choices(languages, [0.75, 0.25])[0]

    choice = "en-US,en;q=0.5"
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
