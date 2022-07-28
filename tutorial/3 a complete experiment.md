# A Complete Experiment
## Updating and Deployment Using Airflow
This section will aim to take the reader from a static setup to one that allows for
automated updates to crawlers and the automation of all processes.
We begin with the setup from the previous section "a more complete setup" and extend it.

### Updating
Updating crawler preferences requires two components. First, we need to alter the Crawler.update_crawler 
and Config.update_config methods. Second we need to parse the reports that are relevant
for any updating behavior and pass this to these functions.

So, as before, we re-define the methods in the "worker/classes" file.
First the update method for the Config object.
```python

```
