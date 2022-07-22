# First Steps
We begin by creating a new experiment with a single crawler and assigning it a task.
For the time being we will simply use the base classes found in src/base. Begin by importing
the base crawler and base configurations object.

`
from src.base.BaseCrawler import BaseCrawler
from src.base.BaseConfig import BaseConfig
`

We do need some input data. In particular, py checks whether Geosurf proxies and their
locations are valid. To do so, we need to download a list of valid cities from our
s3 bucket. To do so, load the s3 module

