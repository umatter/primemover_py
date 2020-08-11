import math


def media_utility_u_ij(d_tilde_ij, ro_j, epsilon_ij, alpha_tilde, tau_tilde_ij=1):
    """
    :param d_tilde_ij: float > 0, ideological distance |pi_i-pi_tilde_j| where pi_i
        represents the political orientation of the individual and pi_tilde_j
        that of outlet j
    :param ro_j: float >= 0, reach of outlet j
    :param epsilon_ij: float, noise/error
    :param alpha_tilde: float >= 0, shift parameter
    :param tau_tilde_ij: float > 0, "transportation costs" i.e. costs of consuming
        ideologicaly distant news
    :return u: float > 0, utility  derived by individual i when consuming news from outlet j
    """
    u = alpha_tilde - tau_tilde_ij * d_tilde_ij + ro_j + epsilon_ij
    return u


def search_utility_v_ik(d_hat_ik, epsilon_ik, alpha_hat, tau_hat_ik=1):
    """
    :param d_hat_ik: float > 0, ideological distance |pi_i-pi_hat_k| where pi_i
        represents the political orientation of the individual and pi_hat_j
        that of search term j
    :param epsilon_ik: float, noise/error
    :param alpha_hat: float >= 0, shift parameter
    :param tau_hat_ik: float > 0, "transportation costs" i.e. costs of consuming
        ideologicaly distant news
    :return v: float > 0, utility  derived by individual i when searching phrase k
    """
    v = alpha_hat - tau_hat_ik * d_hat_ik + epsilon_ik
    return v


def political_orientation_pi_i_t(psi_i, kappa_j_t_prev, pi_i_prev, pi_tilde_j_prev):
    """
    :param psi_i: float in [0,1], individuals persuadability
    :param kappa_j_t_prev: binary in {0,1}, indicates  wether ind. can be persuaded
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
    :param utilities: float list, orderd list of individual i's utilities from searching/consuming
            corresponding media
    :return: ordered list of probabilities for each item, determined by probabilistic choice model
    """
    exp_u_list = [math.exp(u) for u in utilities]
    total_exp_u = sum(exp_u_list)
    probabilities = [exp_u/total_exp_u for exp_u in exp_u_list]
    return probabilities

