"""
    This module contains the Experiment class. The experiment object in primemover_py
    contains metadata on an experiment pushed to the api. In particular,
    it contains information on the crawlers involved.
    The api has the optional field preferences, which is used to store the field neutral terms
    available in the Experiment class.
    Note, the experiment dict cannot be pushed using load. Use the dedicated
    update_experiment method in the api_wrapper.
J.L. 03.2021
"""


class Experiment:
    def __init__(self, name='experiment', description='This is an experiment',
                 contact=None, crawlers=None, id=None, neutral_terms=None,
                 preferences=None):
        self.name = name
        self.description = description
        self.contact = contact
        self._crawlers = crawlers
        self._id = id
        self.neutral_terms = neutral_terms
        self._preferences = preferences
        if preferences is not None and type(preferences) is list:
            for pref in preferences:
                if pref.get('name') == 'neutral_terms':
                    self.neutral_terms = pref.get('value')

    @property
    def id(self):
        return self._id

    @property
    def crawlers(self):
        return self._crawlers

    def as_dict(self):
        return_dict = {'name': self.name,
                       'description': self.description,
                       'contact': self.contact,
                       }
        if self._crawlers is not None:
            return_dict['crawlers'] = self.crawlers
        if self._id is not None:
            return_dict['id'] = self.id
        preferences = []
        if self.neutral_terms is not None:
            preferences.append(
                {'name': 'neutral_terms', 'value': self.neutral_terms,
                 'description': 'this lists all neutral terms used by date'})
        if len(preferences) > 0:
            return_dict['preferences'] = preferences
        return return_dict

    @classmethod
    def from_dict(cls, exp_dict):
        if 'data' in exp_dict.keys():
            exp_dict = exp_dict.get('data')
        exp_object = cls(name=exp_dict.get('name'),
                         description=exp_dict.get('description'),
                         contact=exp_dict.get('contact'),
                         id=exp_dict.get('id'),
                         crawlers=exp_dict.get('crawlers'),
                         preferences=exp_dict.get('preferences')
                         )
        return exp_object
