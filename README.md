# primemover_py: A python client library for the primemover configuration appId

## Aim and content

The [primemover_ui](https://github.com/umatter/primemover_ui/) offers a REST API to programmatically configure the initial bot population and update the bot population dynamically while running experiments. This python library serves as a python client software (wrapper) for this API. It has the following functions:

- wrapper functions around the core API methods to interact with the API from Python. (download/parse the bots' JSON configuration files, change a few values, send the updated configuration files to the API)
- specific bot configuration functions that set/update bot behavioral parameter values. For example, bot utility functions. For example, compute a bot's probabilities of visiting certain websites based on a utility function implemented in this python library and parameter values fetched from the REST API, then add these probabilities as parameter values to the bot's configuration file and send the updated configuration to the API.

Overall, this part of the primemover application contains most the economic details/specifications guiding the bot's decisions/behavior.
