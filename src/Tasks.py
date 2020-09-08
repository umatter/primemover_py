import src.Jobs as Jobs

class Tasks:
    def __init__(self, jobs):
        self._jobs = jobs

    def __str__(self):
        return "Job list"

class GoogleSearch(Tasks):
    """
    Conduct a google search and scroll to the bottom of the page
    """
    def __init__(self, term, time, user_id=None, crawler_id=None,
                 config_id=None):
        self._search_term = term
        self._time = time
        jobs = []
        jobs.append(Jobs.VisitWebpageBrowserbar('https://www.google.com',
                                                      start_time=self._time))
        jobs.append(
            Jobs.EnterField(field_name='q', text=self._search_term))
        jobs.append(
            Jobs.ScrollRandom(nr_scroll=4, min_duration=15, max_duration=30,
                              min_pause_duration=0, max_pause_duration=5))
        jobs.append(Jobs.ParseUrls())
        super.__init__(jobs=jobs)

