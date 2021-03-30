from src.worker import Agent, Proxy, ConfigureProfile, Crawler, api_wrapper


def UpdateObject(crawler_list, object_name='agent'):
    object_name = object_name.strip().lower()
    object_dict = {'agent': Agent.Agent,
                   'proxy': Proxy.Proxy,
                   'crawler': Crawler.Crawler,
                   'config': ConfigureProfile.Config}
    if object_name not in object_dict.keys():
        raise ValueError(f'{object_name} is not a valid object')
    if object_name == 'crawler':
        ids = [c.crawler_info.crawler_id for c in crawler_list]
        values = [api_wrapper.fetch_crawler(i) for i in ids ]
    elif object_name == 'proxy':
        ids = [c.proxy.info.proxy_id for c in crawler_list]
        values = [api_wrapper.fetch_proxy(i) for i in ids]
    elif object_name == 'agent':
        ids = [c.agent.info.agent_id for c in crawler_list]
        values = [api_wrapper.fetch_agent(i) for i in ids ]
    elif object_name == 'config':
        ids = [c.configuration.info.configuration_id for c in crawler_list]
        values = [api_wrapper.fetch_config(i) for i in ids]
    else:
        raise Exception('This should not happen!')
    updated_dict = {}
    if object_name!='config':
        for item in values:
            updated_dict[item.get('id')] = object_dict[object_name].from_dict(item)
    else:
        for item in values:
            updated_dict[item.get('id')] = item

    if object_name == 'crawler':
        crawler_list = updated_dict.values()
    elif object_name == 'proxy':
        for c in crawler_list:
            c.proxy = updated_dict[c.proxy.info.proxy_id]
    elif object_name == 'agent':
        for c in crawler_list:
            c.agent = updated_dict[c.agent.info.agent_id]
    elif object_name == 'config':
        for c in crawler_list:
            location = c.agent.location
            c.config = ConfigureProfile.Config.from_dict(updated_dict[c.configuration.info.configuration_id], location)
    else:
        raise Exception('This should not happen!')
    return crawler_list
