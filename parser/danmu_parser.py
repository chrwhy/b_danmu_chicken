import json

#"cmd":"SYS_MSG","msg":"\u7cfb\u7edf\u516c\u544a\uff1a\u300a\u5d29\u574f3\u300b\u590f\u65e5\u76f4\u64ad\u6311\u6218\u6765\u5566\uff01","rep":1,"url":"https:\/\/www.bilibili.com\/blackboard\/activity-bh3summer.html"}
def parse_danmu(danmuStr):
    danmu = json.loads(danmuStr)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(danmu['cmd'])
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    #print(gift['data']['giftName'])
    #print(gift['data']['uname'])
