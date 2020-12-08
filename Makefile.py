import os
import json

if __name__ == "__main__":
    input_val = input('Have you installed all requirements from requirements.txt? (y/n): ')
    if input_val != 'y':
        print('return once all requirements are met')
    else:
        geosurf_username = input('please enter your GEOSURF username: ')
        geosurf_password = input('please enter your GEOSURF password: ')
        keys = {
          "GEOSURF":{
            "username": geosurf_username,
            "password": geosurf_password
          }
        }

        with open('resources/other/keys.json', 'w') as file:
            json.dump(keys, file)

        os.mkdir('resources/crawlers')
        os.mkdir('resources/raw_data')
        os.mkdir('resources/updates')
        os.mkdir('resources/to_push')
        os.mkdir('resources/input_data')

