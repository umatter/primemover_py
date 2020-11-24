import math
import random
import bs4
from urllib.parse import urlparse
from src.worker import api_wrapper
import pandas as pd
import json


def remove_path(url):
    """
    :param url:
    :return: domain
    """
    try:
        split = urlparse(url)
    except TypeError:
        raise TypeError(f'{url} is strange')
    url_cleaned = split.scheme + "://" + split.netloc + '/'
    return url_cleaned


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


def find_results(google_html, selector, attribute='href'):
    """
    :param attribute: href
    :param google_html: google results html file
    :param selector: CSS/XPATH/... In this case selector will be "\"#rso > div > div > div.yuRUbf > a\""
    :return:
    """
    soup = bs4.BeautifulSoup(google_html, "html.parser")
    raw_results = soup.select(selector)
    clean_results = []

    i = 1
    for result in raw_results:
        full_url = result.get(attribute)
        url = remove_path(full_url)
        rank = i
        i += 1
        clean_results.append(
            {'rank': rank, 'full_url': full_url, 'url': url, 'element': result})

    return clean_results


def choose_result(raw_html,
                  outlets_known,
                  all_outlets,
                  pi,
                  alpha_tilde,
                  tau_tilde,
                  beta_i,
                  selector="#rso > div > div > div.yuRUbf > a"):
    """
    :param raw_html: raw html of google search page
    :param beta_i:
    :param tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    :param alpha_tilde: alpha_tilde: float >= 0, shift parameter
    :param selector: str, CSS selector for search results
    :param all_outlets: csv found at https://siaw.qlick.ch/api/v1/outlets"
    :param pi: pi_i  political orientation of the individual (in config)
    :param outlets_known: dict containing outlets of shape: {
      "1011now.com":{
      "pi": 0.4436
      "rho": 0.2}}
    :return: single result item from results list that is to be clicked
    """
    results = find_results(raw_html, selector)

    # calculate utility of each result
    utilities = []
    for result in results:
        # If the url is known to the bot e
        if result['url'] in outlets_known.values():
            # if the url is known to the individual (found in config) set known = 1
            known = 1
            # subtract pi from crawler config and the pi of the media outlet corresponding to the url
            outlet_data = \
            all_outlets.loc[all_outlets['redirect_url'] == result['url']].iloc[
                0]
            d_tilde_i_j_t = abs(
                pi - float(outlet_data['pi']))
            exp_rho = float(outlet_data['avg_reach_permillion'])
            if exp_rho < 0.000000000000000000001:
                exp_rho = 0.000000000000000000001
            rho = math.log(exp_rho)
            # calculate utility of the result
            u = result_utility_w_i_j_t(r_j=result['rank'],
                                       known=known, d_tilde_i_j_t=d_tilde_i_j_t,
                                       rho_j=rho,
                                       alpha_tilde=alpha_tilde,
                                       tau_tilde=tau_tilde,
                                       beta_i=beta_i)
        else:
            u = result_utility_w_i_j_t(result['rank'])
        epsilon = random.uniform(0,1)  # noise parameter
        utilities.append(u + epsilon)
    # convert utilities to probabilites of selecting
    probabilities = prob_i(utilities)
    # conduct experiment_id to select single result
    result = random.choices(results, weights=probabilities, k=1)
    # results_idx = np.random.multinomial(1, probabilities).argmax() (Entspricht dem Paper)

    # return results, click result['element'] und gebe result['full_url'] als behavior zurück.
    return probabilities, result ,results


if __name__ == "__main__":
    # Tests
    outlets = api_wrapper.get_outlets()
    outlets = pd.DataFrame.from_dict(outlets)

    configs = {"id": 763,
               "pi": "-1",
               "psi": "0",
               "kappa": "1",
               "tau": "1",
               "beta": "0.62368980888047",
               "alpha": "0",
               "search_terms": "{\"bigrams\":[\"reproductive health services\",\"equal rights amendment\",\"white supremacist\",\"violence women\",\"law of one\",\"gun safety course\",\"heart attack women\",\"children and family\",\"gun safety course\",\"the dream act\"],\"instagram\":[\"#impeachtrump\",\"#feelthebern\",\"#communism\",\"#impeachtrump\",\"#democracy\",\"#bidenharris\",\"#democracy\",\"#socialism\",\"#bidenharris\",\"#voteblue\"]}",
               "media_outlet_urls": "{\"hillreporter.com\":\"https:\\/\\/hillreporter.com:443\\/\",\"nbcnews.com\":\"https:\\/\\/www.nbcnews.com\\/\",\"pbs.org\":\"https:\\/\\/www.pbs.org\\/\",\"opednews.com\":\"https:\\/\\/www.opednews.com\\/\",\"doinmytoons.blogspot.com\":\"http:\\/\\/doinmytoons.blogspot.com\\/\",\"news.yahoo.com\":\"https:\\/\\/news.yahoo.com\\/\",\"cbsnews.com\":\"https:\\/\\/www.cbsnews.com\\/\",\"esquire.com\":\"https:\\/\\/www.esquire.com\\/\",\"amp.gs\":\"https:\\/\\/amplifr.com\\/en\\/\",\"theroot.com\":\"https:\\/\\/www.theroot.com\\/\"}",
               }
    google_data_1 = api_wrapper.fetch_html(
        "https://siaw.qlick.ch/api/v1/file/228072")
    google_data_2 = api_wrapper.fetch_html(
        "https://siaw.qlick.ch/api/v1/file/227952")
    google_data_3 = api_wrapper.fetch_html(
        "https://siaw.qlick.ch/api/v1/file/227974")
    google_data_4 = api_wrapper.fetch_html(
        "https://siaw.qlick.ch/api/v1/file/227989")
    google_data_5 = api_wrapper.fetch_html(
        "https://siaw.qlick.ch/api/v1/file/228062")
    google_data_6 = api_wrapper.fetch_html("https://siaw.qlick.ch/api/v1/file/198579")
    google_data_7 = api_wrapper.fetch_html("https://siaw.qlick.ch/api/v1/file/198635")
    google_data_8 = api_wrapper.fetch_html("https://siaw.qlick.ch/api/v1/file/201610")
    print(choose_result(google_data_1,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: [0.2886514051574023, 0.2611825921550756, 0.2363277823215377, 0.21383822036598443]
    print(choose_result(google_data_2,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: [0.15054498803265504, 0.13621873826972203, 0.12325581142409145, 0.11152647016690204, 0.1009133233084841, 0.09131015090787677, 0.08262084118795704, 0.07475842861647011, 0.06764422352575242, 0.06120702456008912]
    print(choose_result(google_data_3,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: [0.2418551389405318, 0.21883957945767907, 0.19801424004056156, 0.17917069369265443, 0.1621203478685732]
    print(choose_result(google_data_4,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: [0.16036015604197598, 0.14509986954886514, 0.1312917913199497, 0.1187977254672593, 0.10749262718033964, 0.09726335123576053, 0.0880075196016902, 0.07963249680414247, 0.07205446280001708]
    print(choose_result(google_data_5,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: [0.15054498803265504, 0.13621873826972203, 0.12325581142409145, 0.11152647016690204, 0.1009133233084841, 0.09131015090787677, 0.08262084118795704, 0.07475842861647011, 0.06764422352575242, 0.06120702456008912]
    print(choose_result(google_data_6,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))
    # Probabilities for epsilon = 0: [0.15054498803265504, 0.13621873826972203, 0.12325581142409145, 0.11152647016690204, 0.1009133233084841, 0.09131015090787677, 0.08262084118795704, 0.07475842861647011, 0.06764422352575242, 0.06120702456008912]

    print(choose_result(google_data_7,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))
    # Probabilities for epsilon = 0: ([0.2886514051574023, 0.2611825921550756, 0.2363277823215377, 0.21383822036598443]
    print(choose_result(google_data_8,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        all_outlets=outlets,
                        selector="#rso > div > div > div.yuRUbf > a",
                        pi=float(configs['pi']),
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))
    # Probabilities for epsilon = 0: ([0.2418551389405318, 0.21883957945767907, 0.19801424004056156, 0.17917069369265443, 0.1621203478685732]
