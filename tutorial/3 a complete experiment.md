# A Complete Experiment
## Updating and Deployment Using Airflow
This section will aim to take the reader from a static setup to one that allows for
automated updates to crawlers and the automation of all processes.
We begin with the setup from the previous section "a more complete setup" and extend it.

### Updating
The crawler and configuration object have update methods. By default, the method BaseCrawler.update_crawler
expects a dictionary as displayed below and will pass any information in 'data' to the configuration objects update
function.
```json
{
  "1610": [
    {
      "finished_at": null,
      "status_code": null,
      "status_message": null,
      "flag": "CALCULATED/neutral",
      "data": null,
      "job_id": 1553033
    },
    {
      "finished_at": null,
      "status_code": null,
      "status_message": null,
      "flag": "CALCULATED/neutral",
      "data": null,
      "job_id": 1553040
    }
  ],
  "1611": [
    {
      "finished_at": null,
      "status_code": null,
      "status_message": null,
      "flag": "CALCULATED/neutral",
      "data": null,
      "job_id": 1553095
    }
  ]}
```
