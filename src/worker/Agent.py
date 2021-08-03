"""
Agent class and subclasses. This class mimics the agebt object on the Primemover api
Available Classes:
    - Agent
J.L. 11.2020
"""

from src.worker.Profile import Profile
from src.worker.Info import AgentInfo
import json
import pathlib

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


class Agent:
    """
    Base class
    Public Arguments:
        - info: agent info object
        - multilogin_id: string, should me a valid multilogin id, if it is empty or invalid,
            the runner will assign a new id. This cannot be checked in py and is allways initialy assigned
            by the runner.
        - location: string, Location of the agent.
            Must be an element of valid_cities. formated as  <Nation Abbrev>-<State>-<City>,
              following GEO Surf naming convention.
        - multilogin_profile: Profile object, or escaped, json. Use a profile object to initialize, or json object returned by api.
            See Profile.py for details on structure.
            TODO parse json input for validity by converting to profile first.
    Private Arguments:
        - description: string
        - identification: string, MultiLogin (Not sure why the runner needs this, best not change)
    """
    # Load list of cities to later confirm whether the cities passed will be accepted by the runner
    with open(PRIMEMOVER_PATH + "/resources/other/valid_cities.json",
              'r') as file:
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
        self.multilogin_profile = multilogin_profile
        self._info = info

    @property
    def info(self):
        return self._info

    @property
    def multilogin_id(self):
        return self._multilogin_id

    @multilogin_id.setter
    def multilogin_id(self, val):
        if val is None or val.strip() == "":
            self._multilogin_id = None
        else:
            self._multilogin_id = val

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

    @property
    def multilogin_profile(self):
        return self._multilogin_profile

    @multilogin_profile.setter
    def multilogin_profile(self, val):
        if val is None:
            self._multilogin_profile = Profile()
        elif type(val) is Profile:
            self._multilogin_profile = val
        elif type(val) is str:
            self._multilogin_profile = json.loads(val)
        elif type(val) is dict:
            self._multilogin_profile = val
        else:
            raise TypeError(
                f'multilogin profile must be of type Profile got {type(val)} instead')

    def as_dict(self, send_info=False):
        """
        Output Agent as dict
        """
        return_dict = {"name": self._name,
                       "description": self._description,
                       "location": self._location,
                       "identification": self._identification,
                       "multilogin_id": self._multilogin_id,
                       "multilogin_profile": self._multilogin_profile}
        if type(self._multilogin_profile) is Profile:
            return_dict["multilogin_profile"] = (
                self._multilogin_profile.as_dict())

        if send_info and self._info is not None:
            for key, value in self._info.as_dict().items():
                return_dict[key] = value
        return return_dict

    @classmethod
    def from_dict(cls, agent_dict):
        if type(agent_dict) is list:
            agent_dict = agent_dict[0]
        elif type(agent_dict) is str:
            agent_dict = json.loads(agent_dict)
        agent_object = cls(name=agent_dict.get('name'),
                           description=agent_dict.get('description'),
                           identification=agent_dict.get('identification'),
                           multilogin_id=agent_dict.get('multilogin_id'),
                           multilogin_profile=Profile.from_dict(json.loads(agent_dict.get(
                               'multilogin_profile'))),
                           location=agent_dict.get('location'),
                           info=AgentInfo.from_dict(agent_dict))
        return agent_object

if __name__ == '__main__':
    from src.worker import api_wrapper as api
    with open(PRIMEMOVER_PATH + '/resources/other/keys.json', 'r') as f:
        KEYS = json.load(f)
    key = api.get_access(KEYS['PRIMEMOVER']['username'],
                         KEYS['PRIMEMOVER']['password'])
    for id in range(1550, 1800):
        file = api.fetch_agent(id)
        test = Agent.from_dict(file)
        comp = json.loads(file['multilogin_profile'])
        prof = Profile.from_dict(json.loads(file['multilogin_profile']))
        assert comp == prof.as_dict(), f'Oh No! {id},\n {comp} \n {prof}'
