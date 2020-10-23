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
    probabilities = [exp_u / total_exp_u for exp_u in exp_u_list]
    return probabilities


def result_utility_w_i_j_t(r_j, known=0, d_tilde_i_j_t=0, rho_j=0,
                           alpha_tilde=1,
                           tau_tilde=1, beta_i=0.1):
    """
    :param known: indicates whether or not individual knows the outlet.
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
            r_j - 1)) + known * (
                    alpha_tilde - tau_tilde * d_tilde_i_j_t + rho_j)

    return w


def find_results(selector, google_html, attribute):
    """
    :param google_html: google results html file
    :param selector: CSS/XPATH/... In this case selector will be "\"#rso > div > div > div.yuRUbf > a\""
    :return:
    """
    raw_results = find_all_results_in_html_by_CSS(selector)
    clean_results = []
    i = 1
    for result in raw_results:
        full_url = get_attribute(result, attribute)  # usually href
        url = remove_path(raw_url)
        rank = i
        i += 1
        clean_results.append(
            {'rank': rank, 'full_url': full_url, 'url': url, 'element': result})

    return clean_results


def choose_result(raw_html, outlets_known, all_outlets):
    """
    :param all_outlets: csv found at https://siaw.qlick.ch/api/v1/outlets"
    :param pi: pi_i  political orientation of the individual (in config)
    :param results: list of results found when using
    :param outlets_known: dict containing outlets of shape: {
      "1011now.com":{
      "pi": 0.4436
      "rho": 0.2}}
    :return: single result item from results list that is to be clicked
    """
    results = find_results(raw_html)

    # calculate utility of each result
    utilities = []
    for result in results:
        # If the url is somewhere in the outlets database
        if result['url'] in all_outlets['url']:
            # if the url is known to the individual (found in config) set known = 1
            known = 1 * (result_url in outlets_known['url'])
            # subtract pi from crawler config and the pi of the media outlet corresponding to the url
            d_tilde_i_j_t = abs(
                pi - all_outlets[all_outlets['url'] == result_url]['pi'])
            # calculate utility of the result
            u = result_utility_w_i_j_t(r_j=result['rank'],
                                       known=known, d_tilde_i_j_t=d_tilde_i_j_t,
                                       rho_j=all_outlets[
                                           all_outlets['url'] == result_url][
                                           'rho'],
                                       alpha_tilde="in crawler_config",
                                       tau_tilde="in crawler_config",
                                       beta_i="in crawler_config")
        else:
            u = result_utility_w_i_j_t(rank)
        epsilon = random.uniform(0, 1)  # noise parameter
        utilities.append(u + epsilon)
    # convert utilities to probabilites of selecting
    probabilities = prob_i(utilities)
    # conduct experiment_id to select single result
    # Muss nicht so gemacht werden. Ich habe das nur aus konsistenz zum paper so gemacht. Es ist equivalent einfach ein outlet aus einer Liste mit den Gewiichten aus probabilities zu ziehen.
    # e.g. random.choices(results, weights=probabilities, k=1) (Macht bei einem einzelnen experimeent das selbe und ist sicher einfacher als funktion zu finden)
    results_idx = np.random.multinomial(1, probabilities).argmax()

    # return results, click result['element'] und gebe result['full_url'] als behavior zurück.
    return results
