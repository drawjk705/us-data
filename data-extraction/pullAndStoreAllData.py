from utils import getDatafromApi, joinData
from constants import DATA_FILES_DIR, codes

for topic, topicDict in codes.items():
    print(topic, end='...')

    topicCodes = list(topicDict.values())
    topicTitles = list(topicDict.keys())
    codesAndTitles = list(zip(topicCodes, topicTitles))

    apiData = getDatafromApi(codesAndTitles)

    df = joinData(apiData)

    df.to_csv(f'{DATA_FILES_DIR}/{topic}.csv', index=False)
    print(' done')
