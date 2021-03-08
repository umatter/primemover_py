import math
import random
from numpy import random as np_random
from urllib.parse import urlparse
from src.worker import api_wrapper
import json
from lxml import etree


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


def result_utility_w_i_j_t(r_j,beta_i, known=0, d_tilde_i_j_t=0,
                           alpha_tilde=1,
                           tau_tilde=1):
    """
    :param known: indicates whether or not individual knows the outlet.
    :param beta_i:
    :param r_j: int > 0 rank of outlet in search engine result list
    :param d_tilde_i_j_t: float > 0, ideological distance |pi_i-pi_tilde_j| where pi_i
        represents the political orientation of the individual and pi_tilde_j
        that of outlet j
    :param alpha_tilde: float >= 0, shift parameter
    :param tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    :return: float utility of selecting result
    """


    w = (1 - beta_i * (
            r_j - 1)) + known * (
                alpha_tilde - tau_tilde * d_tilde_i_j_t ** 2)

    return w


def find_results(google_html, x_path, attribute='a.href'):
    """
    :param attribute: href
    :param google_html: google results html file
    :param selector: CSS/XPATH/... In this case selector will be "\"#rso > div > div > div.yuRUbf > a\""
    :return:
    """
    htmlparser = etree.HTMLParser()
    tree = etree.fromstring(google_html, htmlparser)
    raw_results = tree.xpath(x_path)
    clean_results = []
    attribute = 'href'
    i = 1
    for result in raw_results:
        full_url = result.attrib[attribute]
        url = remove_path(full_url)
        rank = i
        i += 1
        clean_results.append(
            {'rank': rank, 'full_url': full_url, 'url': url, 'element': result})

    return clean_results


def choose_result(raw_html,
                  outlets_known,
                  pi,
                  alpha_tilde,
                  tau_tilde,
                  beta_i,
                  x_path='.//div[@class="yuRUbf"]/a'):
    """
    :param raw_html: raw html of google search page
    :param beta_i:
    :param tau_tilde: float > 0, "transportation costs" i.e. costs of consuming
        ideologically distant news
    :param alpha_tilde: alpha_tilde: float >= 0, shift parameter
    :param selector: str, CSS selector for search results
    :param pi: pi_i  political orientation of the individual (in config)
    :param outlets_known: list containing outlets of shape:     #ÄNDERUNG
        [{"url": "https://www.1011now.com/",
          "pi": 0.4436,
          "rho": 0.2,
          "domain":1011now.com},
     {"url": ...},...]
    :return: single result item from results list that is to be clicked
    """

    results = find_results(raw_html, x_path)
    outlets_known_url = [x['url'] for x in outlets_known]
    # calculate utility of each result
    utilities = []
    for result in results:
        # If the url is known to the bot e
        if result['url'] in outlets_known_url:
            # if the url is known to the individual (found in config) set known = 1
            known = 1
            # subtract pi from crawler config and the pi of the media outlet corresponding to the url
            # This will be fetchable from the crawler config.
            pi_outlet = None
            for outlet in outlets_known:
                if outlet['url'] == result['url']:
                    pi_outlet = outlet['pi']
            if pi_outlet is None:
                known = 0
                d_tilde_i_j_t = 0
            else:
                d_tilde_i_j_t = abs(pi - float(pi_outlet))


            # calculate utility of the result
            u = result_utility_w_i_j_t(r_j=result['rank'],
                                       known=known,
                                       d_tilde_i_j_t=d_tilde_i_j_t,
                                       # rho_j=rho,
                                       alpha_tilde=alpha_tilde,
                                       tau_tilde=tau_tilde,
                                       beta_i=beta_i)

        else:
            u = result_utility_w_i_j_t(result['rank'], beta_i)
            # HIER IST EINE VERÄNDERUNG#
            # jetzt "Gumbel" verteilt mit mu = 0.4557735 (vllt. als 'location' angeführt),
            # beta = 0.793006( vllt. als 'scale' angeführt) (1 = Anzahl Werte)
        epsilon = np_random.gumbel(-0.4557735, 0.793006, 1)  # noise parameter
        utilities.append(u + epsilon)
    # convert utilities to probabilites of selecting
    probabilities = prob_i(utilities)
    # conduct experiment_id to select single result
    result = random.choices(results, weights=probabilities, k=1)

    return result


if __name__ == "__main__":
    # Tests

    configs = {"id": 763,
               "pi": "-1",
               "psi": "0",
               "kappa": "1",
               "tau": "1",
               "beta": "0.62368980888047",
               "alpha": "0",
               "search_terms": "{\"bigrams\":[\"reproductive health services\",\"equal rights amendment\",\"white supremacist\",\"violence women\",\"law of one\",\"gun safety course\",\"heart attack women\",\"children and family\",\"gun safety course\",\"the dream act\"],\"instagram\":[\"#impeachtrump\",\"#feelthebern\",\"#communism\",\"#impeachtrump\",\"#democracy\",\"#bidenharris\",\"#democracy\",\"#socialism\",\"#bidenharris\",\"#voteblue\"]}",
               "media_outlet_urls": '[{"domain": "hillreporter.com", "url": "https://hillreporter.com:443/", "pi": -0.9}, {"domain": "nbcnews.com", "url": "https://www.nbcnews.com/", "pi": 0.1}, {"domain": "pbs.org", "url": "https://www.pbs.org/", "pi": -0.3}, {"domain": "opednews.com", "url": "https://www.opednews.com/", "pi": -0.4}, {"domain": "doinmytoons.blogspot.com", "url": "http://doinmytoons.blogspot.com/", "pi": -0.2}, {"domain": "news.yahoo.com", "url": "https://news.yahoo.com/", "pi": 0.0}, {"domain": "cbsnews.com", "url": "https://www.cbsnews.com/", "pi": 0.1}, {"domain": "esquire.com", "url": "https://www.esquire.com/", "pi": 0.01}]',
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
    # google_data_6 = api_wrapper.fetch_html(
    #     "https://siaw.qlick.ch/api/v1/file/198579")
    # google_data_7 = api_wrapper.fetch_html(
    #     "https://siaw.qlick.ch/api/v1/file/198635")
    # google_data_8 = api_wrapper.fetch_html(
    #     "https://siaw.qlick.ch/api/v1/file/201610")

    # Dieses Beispiel ist äquivalent zu dem job 6883 (der Bot kennt kein Resultat und hat die selben Parameter
    print(choose_result(google_data_2,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        x_path='.//div[@class="yuRUbf"]/a',
                        pi=0,
                        alpha_tilde=0.26080780865406,
                        tau_tilde=1,
                        beta_i=0.084178134402416))
    # Probabilities for epsilon = 0: [0.14187049056381099, 0.13041692953080028, 0.1198880432473838, 0.11020918039856238, 0.10131171645749518, 0.09313256712775438, 0.0856137410666087, 0.07870192871807996, 0.07234812434053928, 0.066507278548965]
    # Utilities for epsilon = 0: [1.0, 0.915821865597584, 0.831643731195168, 0.7474655967927519, 0.663287462390336, 0.57910932798792, 0.49493119358550397, 0.4107530591830879, 0.32657492478067196, 0.242396790378256]
    print(choose_result(google_data_2,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        pi=float(configs['pi']),
                        x_path='.//div[@class="yuRUbf"]/a',
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: ([0.46494621152355536, 0.24919405140781364, 0.1335588369535387, 0.07158261935871645, 0.03836564851217897, 0.02056257509080419, 0.011020783194391695, 0.0059067340389727585, 0.0031657919761014955, 0.0016967479439266545]
    # Utilities for epsilon = 0: [1.0, 0.37631019111953, -0.24737961776093997, -0.8710694266414101, -1.49475923552188, -2.11844904440235, -2.74213885328282, -3.36582866216329, -3.98951847104376, -4.61320827992423]
    print(choose_result(google_data_3,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        pi=float(configs['pi']),
                        x_path='.//div[@class="yuRUbf"]/a',
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: ([0.25208597380233444, 0.3747204893546746, 0.2008363861742727, 0.10764090877711281, 0.02080120587295234, 0.011148680507930943, 0.016572278705464877, 0.00888213124297069, 0.00476049533196304, 0.0025514502303235873]
    # Utilities for epsilon =0:[-0.020100000000000007, 0.37631019111953, -0.24737961776093997, -0.8710694266414101, -2.5148592355218797, -3.1385490444023496, -2.74213885328282, -3.36582866216329, -3.98951847104376, -4.61320827992423]
    print(choose_result(google_data_4,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        pi=float(configs['pi']),
                        x_path='.//div[@class="yuRUbf"]/a',
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: ([0.4657364488856138, 0.24961758953963298, 0.13378583779875025, 0.07170428345423815, 0.03843085598806005, 0.02059752389712662, 0.011039514467866997, 0.0059167733119244465, 0.0031711726567867347]
    # Utilities for epsilon = 0: [1.0, 0.37631019111953, -0.24737961776093997, -0.8710694266414101, -1.49475923552188, -2.11844904440235, -2.74213885328282, -3.36582866216329, -3.98951847104376]
    print(choose_result(google_data_5,
                        outlets_known=json.loads(configs['media_outlet_urls']),
                        pi=float(configs['pi']),
                        x_path='.//div[@class="yuRUbf"]/a',
                        alpha_tilde=float(configs['alpha']),
                        tau_tilde=float(configs['tau']),
                        beta_i=float(configs['beta'])))

    # Probabilities for epsilon = 0: ([0.46494621152355536, 0.24919405140781364, 0.1335588369535387, 0.07158261935871645, 0.03836564851217897, 0.02056257509080419, 0.011020783194391695, 0.0059067340389727585, 0.0031657919761014955, 0.0016967479439266545]
    # Utilities for epsilon = 0: [1.0, 0.37631019111953, -0.24737961776093997, -0.8710694266414101, -1.49475923552188, -2.11844904440235, -2.74213885328282, -3.36582866216329, -3.98951847104376, -4.61320827992423]
