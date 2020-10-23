from src.worker.Crawler import *
from src.GenerateBenignTerms import GenerateBenignTerms
from src.worker.TimeHandler import Schedule
from datetime import datetime, timedelta
import src.worker.api_wrapper as api

PATH_TERMS = "resources/input_data/insta_top_partisan_hashtags.csv"
PATH_MEDIA_OUTLETS = "resources/input_data/twitter_stream_top_partisan_domains.csv"
PATH_BENGING_TERMS = 'resources/other/benign_terms.json'

NEUTRAL = ["White House", "Congress", "Mail-in ballot", "Polling station",
           "Joe Biden", "Donald Trump", "Democrat", "Republican"]

if __name__ == "__main__":
    GenerateBenignTerms()

    # existing_crawler_path = f'resources/updates/exp_2_{(datetime.now().date()+ timedelta(days=-1)).isoformat()}.json'
    existing_crawler_path = "resources/crawlers/2020-10-23.json"
    TimeHandler.GLOBAL_SCHEDULE = Schedule(start_at=10 * 60 * 60,
                                           end_at=(10 + 23) * 60 * 60)


    Config.MEDIA_DEFAULT_PATH = PATH_MEDIA_OUTLETS
    Config.TERM_DEFAULT_PATH = PATH_TERMS

    with open(existing_crawler_path, 'r') as file:
        raw_crawlers = json.load(file)
    crawler_list_combined = Crawler.from_list(raw_crawlers)
    crawler_list_neutral = []
    crawler_list_political = []
    for crawler in crawler_list_combined:
        if crawler.flag in {'right', 'left'}:
            crawler_list_political.append(crawler)
        else:
            crawler_list_neutral.append(crawler)

    neutral = r.choices(NEUTRAL, k=2)
    with open(PATH_BENGING_TERMS, 'r') as file:
        benign = json.load(file)

    for individual in crawler_list_political:
        # 3 Twitter, 3 Domain, 3 bigram
        # 2 Most visited
        # 1-2 benign
        # 2 test
        # 3 Politial, 1 most visited, 1 direct
        nr_direct = r.choices([0, 1, 2])
        session_id = individual.add_task(PoliticalSearchNoUtility,
                                         to_session=True,
                                         params={'term_type': 'bigrams'})
        if r.choice([True, False]):
            individual.add_task(BenignGoogleSearch, to_session=session_id,
                                params={'term': r.choice(benign)})
        individual.add_task(VisitMediaNoUtility, to_session=session_id)
        individual.add_task(PoliticalSearchNoUtility, to_session=session_id,
                            params={'term_type': 'instagram'})
        individual.add_task(VisitMediaGoogleNoUtility, to_session=session_id)
        individual.add_task(VisitFrequentDirect, to_session=session_id)
        if nr_direct == 2:
            nr_direct -= 1
            individual.add_task(VisitMediaNoUtility, to_session=session_id)

        individual.add_task(PoliticalSearchNoUtility, to_session=session_id,
                            params={'term_type': 'bigrams'})
        individual.add_task(VisitMediaNoUtility, to_session=session_id)
        individual.add_task(PoliticalSearchNoUtility, to_session=session_id,
                            params={'term_type': 'instagram'})
        individual.add_task(VisitMediaGoogleNoUtility, to_session=session_id)
        individual.add_task(VisitFrequentDirect, to_session=session_id)

        if nr_direct == 1:
            individual.add_task(VisitMediaNoUtility, to_session=session_id)
        individual.add_task(PoliticalSearchNoUtility, to_session=session_id,
                            params={'term_type': 'bigrams'})
        individual.add_task(PoliticalSearchNoUtility, to_session=session_id,
                            params={'term_type': 'instagram'})
        individual.add_task(VisitMediaGoogleNoUtility, to_session=session_id)
        individual.add_task(VisitMediaNoUtility, to_session=session_id)
        individual.add_task(BenignGoogleSearch, to_session=session_id,
                            params={'term': r.choice(benign)})

        individual.add_task(NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[0]})
        individual.add_task(NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[1]})

    for individual in crawler_list_neutral:
        session_id = individual.add_task(VisitFrequentDirect, to_session=True)
        if r.choice([True, False]):
            individual.add_task(BenignGoogleSearch, to_session=session_id,
                                params={'term': r.choice(benign)})
        individual.add_task(VisitFrequentDirect, to_session=session_id)
        individual.add_task(BenignGoogleSearch, to_session=session_id,
                            params={'term': r.choice(benign)})
        individual.add_task(NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[0]})
        individual.add_task(NeutralGoogleSearch, to_session=session_id,
                            params={'term': neutral[1]})

    crawler_list = crawler_list_neutral + crawler_list_political

    with open("resources/examples/test_update_py.json", 'w') as file:
        json.dump([crawler.as_dict() for crawler in crawler_list], file,
                  indent='  ')

    return_data = api.push_new(path="resources/examples/test_update_py.json")
    data_as_dict = json.loads(return_data.text)
    with open(
            f'resources/updates/exp_2_{datetime.now().date().isoformat()}.json',
            'w') as file:
        json.dump(data_as_dict, file, indent='  ')
