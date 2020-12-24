from utils.loadDataFile import DIR
from utils.getDataFromApi import getDatafromApi
from utils.joinData import joinData
from constants import codes

for topic, topicDict in codes.items():
    print(topic, end='...')

    topicCodes = list(topicDict.values())
    topicTitles = list(topicDict.keys())
    codesAndTitles = list(zip(topicCodes, topicTitles))

    apiData = getDatafromApi(codesAndTitles)

    df = joinData(apiData)

    df.to_csv(f'{DIR}/{topic}.csv', index=False)
    print(' done')
