import json

def parse_danmu(danmuStr):
    danmu = json.loads(danmuStr)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(danmu['cmd'])
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    #print(gift['data']['giftName'])
    #print(gift['data']['uname'])
