import src.Behavior as Behavior


class Jobs:

    def __init__(self,
                 id=None,
                 queue_id=None,
                 name="",
                 description="",
                 order=1,
                 active=1,
                 user_id=None,
                 started=0,
                 failure=0,
                 crawler_id=None,
                 start_at=None,
                 success=0):
        self._id = id
        self._queue_id = queue_id
        self._description = description
        self._user_id = user_id
        self._started = started
        self._failure = failure
        self._order = order
        self._crawleer_id = crawler_id
        self._start_at = start_at
        self._name = name
        self._success = success
        self._active = active
        self.behaviors = [Behavior.JobType(name.replace('-', ), self._active)]
        if start_at is not None:
            self.behaviors.append(Behavior.StartTime(start_at))

    @property
    def behaviors(self):
        return self._behaviors

    @behaviors.setter
    def behaviors(self, behavior_list):
        type_list = [type(behavior) for behavior in behavior_list]
        if Behavior.JobType not in type_list:
            raise ValueError(
                'The first element of behviors must be of class JobType')
        else:
            self._behaviors = behavior_list

    def __str__(self):
        job_descr = f'"id": {self._id},\n "user_id": {self._user_id},\n"queue_id": {self._queue_id},\n"name": "{self._name}",\n"description": "{self._description}",\n"started": {self._started},\n"success": {self._success}, "failure": {self._failure},"order": {self._order},\n"active": {self._active}'
        formatted = ",\n".join([str(x) for x in self.behaviors])
        return f'{{{job_descr},"behaviors": [\n{formatted}]}}'


class EnterField(Jobs):

    def __init__(self, field_name, text, css="", x_path=""):
        super().__init__(name="Enter Field",
                         description="JobType  a  term  into  a  (search)  field  on  the  page  currently  open  in  the  browser  and  hit  enter  (for  example,  the current page open in the browser is google.com, select the search field, kind a term into it, hit enter).  (with human-like typing and cursor movements)",
                         )
        self._behaviors.append(Behavior.Field(field_name))

        self.behaviors.append(Behavior.Text(text))

        self.behaviors.append(Behavior.CSS(css))

        self.behaviors.append(Behavior.XPath(x_path))


class EnterFieldButton(Jobs):
    def __init__(self, text, css_field="", x_path_field="", css_button="",
                 x_path_button=""):
        super().__init__(name="Enter Field Button",
                         description="JobType a term into a (search) field on the page currently open in the browser and submit by clicking on a button.  Same job as enter_field, but using a button on the page instead of hitting enter. (with human-like typing and cursor movements).")

        if x_path_button.strip() == css_button.strip() == "":
            raise ValueError('x_path and css can\'t both be blank')

        if x_path_field.strip() == css_field.strip() == "":
            raise ValueError('x_path and css can\'t both be blank')

        self.behaviors.append(Behavior.Text(text))

        self.behaviors.append(Behavior.CSS(css_field, 'field'))

        self.behaviors.append(Behavior.XPath(x_path_field, 'field'))

        self.behaviors.append(Behavior.CSS(css_button, 'button'))

        self.behaviors.append(Behavior.XPath(x_path_button, 'button'))


class Login(Jobs):
    def __init__(self, username, password, css_password="", x_path_password="",
                 css_username="",
                 x_path_username=""):
        super().__init__(name="Log-in",
                         description="Log in to a page. (human-like cursor movement and typing)")

        if username.strip() == css_username.strip() == "":
            raise ValueError('x_path and css can\'t both be blank')

        if x_path_password.strip() == css_password.strip() == "":
            raise ValueError('x_path and css can\'t both be blank')

        self.behaviors.append(Behavior.Username(username))

        self.behaviors.append(Behavior.Password(password))

        self.behaviors.append(Behavior.CSS(css_password, 'password'))

        self.behaviors.append(Behavior.XPath(x_path_password, 'password'))

        self.behaviors.append(Behavior.CSS(css_username, 'username'))

        self.behaviors.append(Behavior.XPath(x_path_username, 'username'))


class ParseUrls(Jobs):
    def __init__(self, x_path="", css=""):
        super().__init__(name="Parse URLs",
                         description="Parse and cache (all/specific) URLs found in the current webpage (open in browser).")

        self.behaviors.append(Behavior.CSS(css))

        self.behaviors.append(Behavior.XPath(x_path))


class RestRandom(Jobs):
    def __init__(self, min_duration, max_duration):
        super().__init__(name="REST random",
                         description=f'Rest for between {min_duration}, {max_duration} seconds')

        self.behaviors.append(Behavior.Duration(min_duration, max_duration))


class ScrollRandom(Jobs):
    def __init__(self, nr_scroll, min_duration, max_duration,
                 min_pause_duration, max_pause_duration):
        super().__init__(name="Scroll random",
                         description=f'Systematically scroll down/up in an open page (in order to ’get somewhere’ on the page). (human-like scrolling)')

        self.behaviors.append(
            Behavior.PauseInterval(min_duration=min_pause_duration,
                                   max_duration=max_pause_duration))
        self.behaviors.appennd(Behavior.NoOfScrolls(nr_scroll))
        self.behaviors.append(Behavior.Duration(min_duration, max_duration))


class SelectURL(Jobs):
    def __init__(self, x_path, css):
        super().__init__(name="Scroll random",
                         description=f'Select a specific link with the cursor (human-like cursor movement).  That is, open a webpage by clicking on a URL or a field/image/button etc.  in the currently loaded page.')
        if x_path.strip() == css.strip() == "":
            raise ValueError('x_path and css can\'t both be blank')
        self.behaviors.append(Behavior.XPath(x_path))
        self.behaviors.append(Behavior.CSS(css))


class VisitWebpageBrowserbar(Jobs):
    def __init__(self, url, start_time, probability=1):
        super().__init__(name="Visit webpage browserbar",
                         description="Open webpage by typing URL into web browser bar",
                         start_at=start_time)
        self.behaviors.append(Behavior.URL(url))
        self.behaviors.append(Behavior.ActiveProbability(probability))


class VisitWebpageFavorites(Jobs):
    def __init__(self, url, favorites_url_id, start_time, probability=1):
        super().__init__(name="Visit webpage favorites",
                         description="Open webpage by selecting URL from browser favorites.",
                         start_at=start_time)
        self.behaviors.append(Behavior.URL(url))
        self.behaviors.append(Behavior.ActiveProbability(probability))
        self.behaviors.append(Behavior.UrlId(favorites_url_id, 'favorites'))


class VisitWebpageHistory(Jobs):
    def __init__(self, url, history_url_id, start_time, probability=1):
        super().__init__(name="Visit webpage history",
                         description="Open webpage by selecting URL from browser history.",
                         start_at=start_time)
        self.behaviors.append(Behavior.URL(url))
        self.behaviors.append(Behavior.ActiveProbability(probability))
        self.behaviors.append(Behavior.UrlId(history_url_id, 'history'))


if __name__ == "__main__":
    test = EnterField('q', 'hello world')
    print(test)
