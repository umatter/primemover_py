"""
Use this file or copies of it to control how the Config class generates user profiles

J.L. 11.2020
"""

import random as r
import pandas as pd


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


def SelectSearchTerms(pi):
    """
    Select a subset of all search terms. Terms come from two sepparate pools of terms.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of term lists with keys 'instagram' and 'bigrams' denoting the source of each list.
    """
    path_terms_instagram = 'resources/input_data/insta_top_partisan_hashtags.csv'
    path_terms_bigrams = 'resources/input_data/most_partisan_searchterms_pool.csv'
    terms_instagram = pd.read_csv(path_terms_instagram)
    terms_bigrams = pd.read_csv(path_terms_bigrams)
    if pi == -1:
        terms_instagram = terms_instagram.loc[terms_instagram['party'] == 'D']
        terms_bigrams = terms_bigrams.loc[terms_bigrams['party'] == 'D']
    elif pi == 1:
        terms_instagram = terms_instagram.loc[terms_instagram['party'] == 'R']
        terms_bigrams = terms_bigrams.loc[terms_bigrams['party'] == 'R']
    else:
        return {'bigrams': [], 'instagram': []}
    indexes_bigram = r.choices(terms_bigrams.index, k=10)
    indexes_insta = r.choices(terms_instagram.index, k=10)
    terms = {
        'bigrams': terms_bigrams.loc[indexes_bigram]['search_term'].tolist(),
        'instagram': terms_instagram.loc[indexes_insta]['hashtag'].tolist()}
    return terms


def SelectMediaOutlets(pi=0):
    """
    Select a subset of all media outlets.
    Arguments:
        - pi: political orientation of individual
    Returns: dictionary of outlets with domains as keys and urls as values
    """
    PATH_MEDIA_OUTLETS = 'resources/input_data/twitter_stream_top_partisan_domains.csv'
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
