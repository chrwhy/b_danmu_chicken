import simplejson

#"cmd":"SYS_MSG","msg":"\u7cfb\u7edf\u516c\u544a\uff1a\u300a\u5d29\u574f3\u300b\u590f\u65e5\u76f4\u64ad\u6311\u6218\u6765\u5566\uff01","rep":1,"url":"https:\/\/www.bilibili.com\/blackboard\/activity-bh3summer.html"}

#COMBO_END
#ROOM_BLOCK_MSG  禁言

def parse_danmu(danmuStr):
    danmu = simplejson.loads(danmuStr)
    cmd = danmu['cmd']
    print(cmd)
    if cmd == 'DANMU_MSG':
        user_name=danmu['info'][2][1]
        msg=danmu['info'][1]
        danmu_msg = user_name  + ': ' + msg
        print(danmu_msg)
        print('================================n\n')
        return 'DANMAKU_'+danmu_msg
    elif cmd == 'SEND_GIFT':
        gift_name=danmu['data']['giftName']
        user_name=danmu['data']['uname']
        num=danmu['data']['num']
        danmu_msg=user_name  + ' 赠送: ' + gift_name + 'x' + str(num)
        print(danmu_msg)
        print('================================n\n')
        return 'GIFT_'+danmu_msg
    elif cmd == 'WELCOME_GUARD': 
	#{"cmd":"WELCOME_GUARD","data":{"uid":49861834,"username":"387懒癌末末","guard_level":3}}
        #舰长进入直播间
        print(danmuStr)
        print('================================n\n')
        return ''
    elif cmd == 'WELCOME':
        #{"cmd":"WELCOME","data":{"uid":32435143,"uname":"Elucidator丶咲夜","is_admin":false,"svip":1}}
        user_name=danmu['data']['uname']
        print('欢迎 '+user_name)
        print('================================n\n')
        return ''


