import json
from src.worker.Info import AgentInfo


class Agent:
    with open("resources/other/geosurf_cities.json", 'r') as file:
        LOCATION_LIST = list(json.load(file).keys())

    def __init__(self,
                 location=None,
                 name='Agent',
                 description='This is the agent',
                 identification="MultiLogin",
                 multilogin_id=None,
                 multilogin_profile=None,
                 info=None):
        self._name = name
        self._description = description
        self.location = location
        self._identification = identification
        self._multilogin_id = multilogin_id
        self._multilogin_profile = multilogin_profile
        self._info = info

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, val):
        if val in Agent.LOCATION_LIST:
            self._location = val
        else:
            raise ValueError(
                f'{val} is not a valid location see geosurf cities')

    def as_dict(self):
        return_dict = {"name": self._name,
                       "description": self._description,
                       "location": self._location,
                       "identification": self._identification,
                       "multilogin_id": self._multilogin_id,
                       "multilogin_profile": self._multilogin_profile}
        if self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict['key'] = value
        return return_dict

    @classmethod
    def from_dict(cls, agent_dict):
        agent_object = cls(name=agent_dict.get('name'),
                           description=agent_dict.get('description'),
                           identification=agent_dict.get('identification'),
                           multilogin_id=agent_dict.get('multilogin_id'),
                           multilogin_profile=agent_dict.get(
                               'multilogin_profile'),
                           location=agent_dict.get('location'),
                           info=AgentInfo.from_dict(agent_dict))
        return agent_object
