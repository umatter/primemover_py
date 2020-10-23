import random as r
from src.Preferences import *
import json

"""
Use this file or copies of it to control how the Config class generates user profiles
"""

def Psi():
    """
    :return: float in [0,1], individuals persuadability
    """
    return 0


def Pi(flag=None):
    """
    :return pi: political orientation of individual i
    """
    if flag is None or flag == 'political' or flag == 'none':
        return 0
    elif flag == 'left':
        return -1
    elif flag == 'right':
        return 1


def NoiseUtility():
    """
    :return epsilon: float, noise parameter when determining utility
    """
    return r.normalvariate(0, 1)


def SelectSearchTerms(terms_bigrams, terms_instagram, pi):
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
    terms = {'bigrams': terms_bigrams.loc[indexes_bigram]['search_term'].tolist(),
             'instagram': terms_instagram.loc[indexes_insta]['hashtag'].tolist()}
    return terms


def SelectMediaOutlets(outlets_twitter=None, pi=0):
    outlets = {}
    if pi == -1:
        outlets_twitter = outlets_twitter.loc[outlets_twitter['party'] == 'D']
    elif pi == 1:
        outlets_twitter = outlets_twitter.loc[outlets_twitter['party'] == 'R']
    else:
        return {}
    index = r.choices(outlets_twitter.index, k=10)
    for i in index:
        outlets[outlets_twitter.loc[i]['domain']] = outlets_twitter.loc[i]['url']
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

    return None
