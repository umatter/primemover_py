import math
import random
import numpy as np


def media_utility_u_ij(pi_i, pi_tilde_j, rho_j, epsilon_ij, alpha_tilde,
                       tau_tilde_ij=1):
    """
    :param pi_i: float, political orientation of the individual
    :param pi_tilde_j: float, political orientation of the outlet j
    :param d_tilde_ij: float > 0, ideological distance |pi_i-pi_tilde_j| where pi_i
        represents the political orientation of the individual and pi_tilde_j
        that of outlet j
    :param rho_j: float >= 0, reach of outlet j
    :param epsilon_ij: float, noise/errors
    :param alpha_tilde: float >= 0, shift parameter
    :param tau_tilde_ij: float > 0, "transportation costs" i.e. costs of consuming
        ideologicaly distant news
    :return u: float > 0, utility  derived by individual i when consuming news from outlet j
    """
    d_tilde_ij = abs(pi_i-pi_tilde_j)
    u = alpha_tilde - tau_tilde_ij * d_tilde_ij + rho_j + epsilon_ij
    return u


def search_utility_v_ik(pi_i, pi_hat_k, epsilon_ik, alpha_hat=0, tau_hat_ik=1):
    """
    :param pi_hat_k: float, political orientation of the search term k
    :param pi_i: float, political orientation of the individual
    :param epsilon_ik: float, noise/error
    :param alpha_hat: float >= 0, shift parameter
    :param tau_hat_ik: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    :return v: float > 0, utility  derived by individual i when searching phrase k
    """
    d_hat_ik = abs(pi_i-pi_hat_k)
    v = alpha_hat - tau_hat_ik * d_hat_ik + epsilon_ik
    return v


def political_orientation_pi_i_t(psi_i, kappa_j_t_prev, pi_i_prev,
                                 pi_tilde_j_prev):
    """
    :param psi_i: float in [0,1], individuals persuadability
    :param kappa_j_t_prev: binary {0,1}, indicates  whether ind. can be persuaded
        in period t-1
    :param pi_i_prev: political orientation of individual i in period t-1
    :param pi_tilde_j_prev: political orientation of outlet j in period t-1
    :return: pi_i_new: political orientation of individual i in period t, i.e. updated
        political preferences.
    """
    pi_i_new = (
                       1 - psi_i * kappa_j_t_prev) * pi_i_prev + psi_i * kappa_j_t_prev * pi_tilde_j_prev
    return pi_i_new


def prob_i(utilities):
    """
    :param utilities: float list, ordered list of individual i's utilities from searching/consuming
            corresponding media
            or dict with keys and corresponding utilities
    :return: ordered list or dict of probabilities for each item, determined by probabilistic choice model
    """
    if type(utilities) is list:
        exp_u_list = [math.exp(u) for u in utilities]
        total_exp_u = sum(exp_u_list)
        probabilities = [exp_u/total_exp_u for exp_u in exp_u_list]
    elif type(utilities) is dict:
        probabilities = {}
        exp_u_dict = {}
        for key, u in utilities.items():
            exp_u_dict[key] = math.exp(u)
        total_exp_u = sum(exp_u_dict.values())
        for key, exp_u in exp_u_dict:
            probabilities = exp_u/total_exp_u
    else:
        raise TypeError(f'Input must be of type dict or list')
    return probabilities


def result_utility_w_i_j_t(r_j, known=0, d_tilde_i_j_t=0, rho_j=0, alpha_tilde=1,
                           tau_tilde=1, beta_i=0.1):
    """
    :param known: indicates wether or not individual knows the outlet.
    :param beta_i:
    :param r_j: int > 0 rank of outlet in search engine result list
    :param d_tilde_i_j_t: float > 0, ideological distance |pi_i-pi_tilde_j| where pi_i
        represents the political orientation of the individual and pi_tilde_j
        that of outlet j
    :param rho_j: float >= 0, reach of outlet j
    :param alpha_tilde: float >= 0, shift parameter
    :param tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    :return:
    """
    w = (1 - beta_i * (
                r_j - 1)) + known * (alpha_tilde - tau_tilde * d_tilde_i_j_t + rho_j)

    return w


def choose_result(results, outlets, pi):
    """
    :param pi: pi_i  political orientation of the individual
    :param nr_results: int, nr. of results to view
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
    for url, p, rho in outlets.items():
        outlets_dict[url] = {'p': p, 'rho': rho}

    # calculate utility of each result
    utilities = []
    for rank, result_url in results.items():
        if result_url in outlets_dict.keys():
            d_tilde_i_j_t = abs(pi - outlets_dict[result_url]['p'])
            u = result_utility_w_i_j_t(rank, 1, d_tilde_i_j_t, outlets_dict[result_url]['rho'])
        else:
            u = result_utility_w_i_j_t(rank)
        epsilon = random.uniform(0, 1) # noise parameter
        utilities.append(u + epsilon)
    # convert utilities to probabilites of selecting
    probabilities = prob_i(utilities)
    # conduct experiment to select single result
    results_idx = np.random.multinomial(1, probabilities).argmax()

    return results[results_idx]
