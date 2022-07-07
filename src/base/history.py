import src.worker.s3_wrapper as s3_wrapper
from src.base import BaseProfile
import json
from datetime import date


class S3History:
    PROFILE_CLASS = BaseProfile
    def __init__(self, value, fetch_existing=False):
        self.date = date.today().isoformat()
        self._object_class = None
        self._object_id = None
        self.py_object = value
        self._object_name = f'output/history/{self._object_class}/{self._object_id}.json'
        if not fetch_existing:
            self.history = {}
        else:
            self.history = self.pull_existing()
        self._current_status = {}
        self.existing = {}

    def __str__(self):
        return self._object_name

    @property
    def py_object(self):
        return self._py_object

    @py_object.setter
    def py_object(self, value):
        class_name = str(type(value)).split('.')[-1].replace("'>","")
        if class_name in ["Config", "Proxy",
                                "Agent"] and value.info is None:
            raise ValueError(
                f'py_object info is empty! Never create a history for an object not returned by the primemover api!')
        if class_name == "Config":
            self._object_class = 'config'
            self._py_object = value
            self._object_id = value.info.configuration_id
        elif class_name == "Proxy":
            self._object_class = 'proxy'
            self._py_object = value
            self._object_id = value.info.proxy_id

        elif class_name == "Agent":
            self._object_class = 'agent'
            self._py_object = value
            self._object_id = value.info.agent_id
        else:
            raise TypeError('expected object of type CONFIGURATION_FUNCTIONS, Proxy or Agent')

    def update_current_status(self):
        if self._object_class == 'agent':
            self._agent_object()
        elif self._object_class == 'config':
            self._config_object()
        elif self._object_class == 'proxy':
            self._proxy_object()
        self.history[self.date] = self._current_status

    def pull_existing(self):
        exists, io_stream = s3_wrapper.fetch_file_memory(self._object_name)
        if not exists:
            self.existing = {}
        elif len(io_stream.getvalue())==0:
            self._existing = {}
        else:
            io_stream.seek(0)
            self.existing = json.load(io_stream)
            if type(self.existing) != dict:
                raise ValueError(
                    "expected existing File to be a dict of histories")
        self.history = self.existing
        return self.existing

    def push(self):
        # push self to s3
        s3_wrapper.push_dict(self._object_name, self.history)
        return 'success'

    def _agent_object(self):
        self._current_status = {
            "name": self._py_object.name,
            "description": self._py_object.description,
            "location": self._py_object.location,
            "multilogin_id": self._py_object.multilogin_id,
            "multilogin_profile": self._py_object.multilogin_profile}
        if type(self._py_object.multilogin_profile) is self.PROFILE_CLASS:
            self._current_status["multilogin_profile"] = (
                self._py_object.multilogin_profile.as_dict())

    def _proxy_object(self):
        self._current_status = {"name": self._py_object.name,
                                "description": self._py_object.description,
                                "type": self._py_object.type,
                                "hostname": self._py_object.hostname,
                                "port": self._py_object.port}

    def _config_object(self):
        self._current_status = {
            "name": self._py_object.name,
            "description": self._py_object.description,
            "pi": self._py_object.pi,
            "psi": self._py_object.psi,
            "alpha": self._py_object.alpha,
            "tau": self._py_object.tau,
            "kappa": self._py_object.kappa,
            "beta": self._py_object.beta,
            "search_terms": self._py_object.terms,
            "media_outlet_urls": self._py_object.media,
            "location": self._py_object.location
        }
