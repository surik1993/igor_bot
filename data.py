import json

DICT_DATA = 'quiz_data.json'

with open(DICT_DATA, 'r', encoding='utf-8') as j:
        quiz_data = json.loads(j.read())
