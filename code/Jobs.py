import code.Behavior as Behavior


class Jobs:

    def __init__(self,
                 id=None,
                 queue_id=None,
                 name="",
                 description="",
                 order=1,
                 active=1):
        self._id = id
        self._queue_id = queue_id
        self._description = description
        self._order = order
        self.behaviors = [Behavior.Type(name, active)]

    @property
    def behaviors(self):
        return self._behaviors

    @behaviors.setter
    def behaviors(self, behavior_list):
        type_list = [type(behavior) for behavior in behavior_list]
        if Behavior.Type not in type_list:
            raise ValueError('The first element of behviors must be of class Type')
        else:
            self._behaviors = behavior_list


class DownloadFile(Jobs):

    def __init__(self, download_url):
        self.download_url = download_url

