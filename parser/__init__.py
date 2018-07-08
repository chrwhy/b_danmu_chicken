import simplejson

def parse_danmu(danmuStr):
    danmu = simplejson.loads(danmuStr)
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print(danmu['cmd'])
 
