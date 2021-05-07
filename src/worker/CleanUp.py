import os
import pathlib
from datetime import timedelta

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.parent.absolute())


def check_and_delete(path):
    # Check if file @path exists and delete if it does
    if os.path.exists(f'{PRIMEMOVER_PATH}/{path}'):
        os.remove(f'{PRIMEMOVER_PATH}/{path})')
        return True
    else:
        return False


def cleanup(date, nr_days):
    """
    date: datetime object
    nr_days: int, indicates the number of days for which data is to be stored

    deletes files for date - nr_days
    """
    to_delete = date + timedelta(days=-nr_days)
    to_delete = to_delete.date().isoformat()
    # Delete api response
    if check_and_delete('resources/updates/{to_delete}.json'):
        print(f'Deleted update response file for the {to_delete}')
    if check_and_delete('resources/cleaned_data/all_data_{to_delete}.json'):
        print(f'Deleted cleaned data for the {to_delete}')
    # Delete cleaned data with crawlers
    if check_and_delete('resources/cleaned_data/with_crawler_{to_delete}.json'):
        print(f'Deleted cleaned data for the {to_delete}')

    # Delete cleaned Data without Crawlers
    if check_and_delete('resources/cleaned_data/{to_delete}.json'):
        print(f'Deleted cleaned data for the {to_delete}')
