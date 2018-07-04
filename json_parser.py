import json


giftStr = "{\"cmd\":\"SEND_GIFT\",\"data\":{\"giftName\":\"\u8fa3\u6761\",\"num\":10,\"uname\":\"\u5496\u55b1\u829d\u58eb\u5473\u513f\u7684\u97e9\u513f\"}}"
gift = json.loads(giftStr)
print(gift['cmd'])
print(gift['data']['giftName'])
print(gift['data']['uname'])

print('*****************')
print('*****************')

danmuStr = "{\"info\":[[0,1,25,16777215,1530703938,166265622,0,\"425fd67c\",0],\"说好的媚娘呢\",[174162230,\"qazxsswdjkkd\",0,0,0,\"10000\",1,\"\"],[],[12,0,6406234,\">50000\"],[],0,0,{\"uname_color\":\"\"}],\"cmd\":\"DANMU_MSG\"}"
danmu = json.loads(danmuStr)
print(danmu['cmd'])
print(danmu['info'][1])
print(danmu['info'][2][1])

