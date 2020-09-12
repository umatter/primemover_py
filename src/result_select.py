import math
import random
import numpy as np


def prob_i(utilities):
    """
    :param utilities: float list, orderd list of individual i's utilities from searching/consuming
            corresponding media
    :return: ordered list of probabilities for each item, determined by probabilistic choice model
    """
    exp_u_list = [math.exp(u) for u in utilities]
    total_exp_u = sum(exp_u_list)
    probabilities = [exp_u/total_exp_u for exp_u in exp_u_list]
    return probabilities


def result_utility_w_i_j_t(r_j, known=0, d_tilde_i_j_t=0, ro_j=0, alpha_tilde=1,
                           tau_tilde=1, beta_i=0.1):
    """
    :param known: indicates wether or not individual knows the outlet.
    :param beta_i:
    :param r_j: int > 0 rank of outlet in search engine result list
    :param d_tilde_i_j_t: float > 0, ideological distance |pi_i-pi_tilde_j| where pi_i
        represents the political orientation of the individual and pi_tilde_j
        that of outlet j
    :param ro_j: float >= 0, reach of outlet j
    :param alpha_tilde: float >= 0, shift parameter
    :param tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    :return: float utility of selecting result
    """
    w = (1 - beta_i * (
                r_j - 1)) + known * (alpha_tilde - tau_tilde * d_tilde_i_j_t + ro_j)

    return w


def choose_result(results, outlets, pi):
    """
    :param pi: pi_i  political orientation of the individual
    :param results: list of shape: [{rank:int, result_url, x_path...}, {rank:int, result_url,...}]
                assume no missing ranks and first result has rank = 1
    :param outlets: list containing outlets of shape: outlet_prob": [{
      "outlet": "1011now.com",
      "p": 0.4436
      "ro": 0.2
    },
    {
      "outlet": "10news.com",
      "p": 0.3788
      "ro": 0.4
    },
    :return: single result item from results list that is to be clicked
    """
    # reformat outlets data to reflect unique 'outlet' and allow better access
    outlets_dict = {}
    for url, p, ro in outlets.items():
        outlets_dict[url] = {'pi': p, 'ro': ro}

    # calculate utility of each result
    utilities = []
    for rank, result_url in results.items():
        if result_url in outlets_dict.keys():
            d_tilde_i_j_t = abs(pi - outlets_dict[result_url]['p'])
            u = result_utility_w_i_j_t(rank, 1, d_tilde_i_j_t, outlets_dict['ro'])
        else:
            u = result_utility_w_i_j_t(rank)
        epsilon = random.uniform(0, 1) # noise parameter
        utilities.append(u + epsilon)
    # convert utilities to probabilites of selecting
    probabilities = prob_i(utilities)
    # conduct experiment to select single result
    results_idx = np.random.multinomial(1, probabilities).argmax()

    return results[results_idx]
