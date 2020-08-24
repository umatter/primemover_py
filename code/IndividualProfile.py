import Preferences


class Individual:

    def __init__(self, psi, pi, media, terms, results, error_dist):
        self.psi = psi
        self.media = media
        self.terms = terms
        self.results = results
        self.pi = pi
        self.error_dist = error_dist
        self.utility_media = None
        self.utility_search = None
        self.utility_result = None

    def initialize_config(self):
        """
        :return:
        """
        # sample pi from dist or pass pi?
        # set randomness parameters?
        # questions: sample psi if psi!=0

    def initialize_media(self):
        """
        :return:
        """
        # sample media sources from entire list (based on pi?)
        # how many to choose? random, if so what dist?
        # does this exist? if not when?

    def update_config(self, results):
        """
        (if psi >0)
        :param results:
        :return:
        """

    def select_direct(self):
        """
        conducts experiment on media probs. I.e. coin flip for each outlet
        :return: json with direct access
        """

    def select_search_terms(self):
        """
        conducts experiment on search term probs. I.e. coin flip for every term
        :return:
        """

    def select_search_results(self):
        """
        conducts experiment on result ranking util
        :return:
        """
        # Based on utility of result ranking?

    def compile_jobs(self):
        """
        :return:
        """
        # take elements and create jobs (maybe split in smaller portions)
        # compiles file for individual bot, returns a dictionary that looks as desired
        # I have no clue what this is meant to look like
