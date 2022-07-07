from src.worker import api_wrapper


def UpdateObject(crawler_list, desired_object):
    object_name = desired_object.__bases__[0].__name__
    if object_name == 'object':
        object_name = desired_object.__name__

    if object_name not in ["BaseAgent","BaseProxy", "BaseCrawler", "BaseConfig"]:
        raise ValueError(f'{desired_object.__name__} is not a valid object')
    if object_name == 'BaseCrawler':
        ids = [c.crawler_info.crawler_id for c in crawler_list]
        values = [api_wrapper.fetch_crawler(i) for i in ids ]
    elif object_name == 'BaseProxy':
        ids = [c.proxy.info.proxy_id for c in crawler_list]
        values = [api_wrapper.fetch_proxy(i) for i in ids]
    elif object_name == 'BaseAgent':
        ids = [c.agent.info.agent_id for c in crawler_list]
        values = [api_wrapper.fetch_agent(i) for i in ids]
    elif object_name == 'BaseConfig':
        ids = [c.configuration.info.configuration_id for c in crawler_list]
        values = [api_wrapper.fetch_config(i) for i in ids]
    else:
        raise Exception('This should not happen!')
    updated_dict = {}
    if object_name!='BaseConfig':
        for item in values:
            updated_dict[item.get('id')] = desired_object.from_dict(item)
    else:
        for item in values:
            updated_dict[item.get('id')] = item

    if object_name == 'BaseCrawler':
        crawler_list = updated_dict.values()
    elif object_name == 'BaseProxy':
        for c in crawler_list:
            c.proxy = updated_dict[c.proxy.info.proxy_id]
    elif object_name == 'BaseAgent':
        for c in crawler_list:
            c.agent = updated_dict[c.agent.info.agent_id]
    elif object_name == 'BaseConfig':
        for c in crawler_list:
            location = c.agent.location
            c.configuration = desired_object.from_dict(updated_dict[c.configuration.info.configuration_id], location)
    else:
        raise Exception('This should not happen!')
    return crawler_list
