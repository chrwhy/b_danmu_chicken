# coding: utf-8
import random
import os
import _thread
import time
import socket
import requests
import xml.dom.minidom
import struct
import simplejson
from const import BCommand

def _heartbeat(self):
    while True:
        time.sleep(30)
        #xx = struct.pack('!IHHII', length, magic_num, version, msg_type, data_exchange_pack)
        xx = struct.pack('!IHHII', 16, 16, 1, 2, 1)
        print('...........................')
        self.socket_client.send(xx + "".encode('utf-8'))


class DMJBot(object):
    def __init__(self, room_id, u_id=0):
        self.room_id = room_id
        self.api_room_detail_url = 'https://api.live.bilibili.com/api/player?id=cid:{}'.format(room_id)
        self.dm_host = None
        self.socket_client = self._set_up()
        self._uid = u_id or int(100000000000000.0 + 200000000000000.0 * random.random())
        self.magic = 16
        self.ver = 1
        self.into_room = 7
        self.package_type = 1
        self.max_data_length = 65495

        
    def _set_up(self):
        room_detail_xml_string = self._http_get_request(self.api_room_detail_url)
        xml_string = ('<root>' + room_detail_xml_string.strip() + '</root>').encode('utf-8')
        root = xml.dom.minidom.parseString(xml_string).documentElement
        dm_server = root.getElementsByTagName('dm_server')
        self.dm_host = dm_server[0].firstChild.data
        #self.dm_host = '120.92.112.150'

        # tcp_socket return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.dm_host, 2243))
        print(self.dm_host)
        return s

    def _http_get_request(self, url):
        s = requests.session()
        response = s.get(url)
        return response.text

    def _pack_socket_data(self, data_length, data):
        _data = data.encode('utf-8')
        _send_bytes = struct.pack('!IHHII', data_length, self.magic, self.ver, self.into_room, self.package_type)
        return _send_bytes + _data

    def _parse_data(self, json_data):
        if json_data['cmd'] == BCommand.DANMU_MSG:
            pass
        elif json_data['cmd'] == BCommand.SEND_GIFT:
            pass
        elif json_data['cmd'] == BCommand.WELCOME:
            pass

    def _start(self):
        # 是JSON 前面要补16字节数据
        _dmj_data = simplejson.dumps({
            "roomid": self.room_id,
            "uid": self._uid,
        }, separators=(',', ':'))
        total_length = 16 + len(_dmj_data)
        data = self._pack_socket_data(total_length, _dmj_data)
        self.socket_client.send(data)

        # 会断是因为心跳问题，需要30秒内发送心跳
        # 这里先接收确认进入房间的信息
        self.socket_client.recv(16)
        
        _thread.start_new_thread(_heartbeat, (self,))
        
        while True:
            pre_data = self.socket_client.recv(16)
            print(len(pre_data))
            if len(pre_data) < 2:
                print('==========================')
                #sys.exit(-1)
                continue
				
            try:
                data_length, magic, ver, message_type, package_type = struct.unpack('!IHHII', pre_data)
                if data_length < 1:
                    sys.exit(1)
            except struct.error:
                print ('pre_data: ' + pre_data)
                print ('pre_data_len: ' + str(len(pre_data)))
            if(data_length == 16):
                print ('Only control string received, skip it...')
                print (data_length)
                continue
            try:
                print('original--------------------------------------------')
                print('length claimed: ' + str(data_length))
                if data_length>2500:
                    print('********************************')
                    print('********************************')
                    print('********************************')
                    print('********************************')
                    noCtrlStr = self.socket_client.recv(2500)                                           
                else:
                    noCtrlStr = self.socket_client.recv(data_length-16)                                
                if len(noCtrlStr) == 0:
                    sys.exit(1)
                    continue
                print('actual length: ' + str(len(noCtrlStr)))
                #print(noCtrlStr)
                json = noCtrlStr.decode('utf-8')
                print('Json format: ' + json)
                print('original end --------------------------------------------\n\n')
                json_data = simplejson.loads(json)                
            except simplejson.JSONDecodeError:
                print ('json error=======================================')				
                print(json)
                #print(data)
                #print (data[16:].decode('utf-8'))
                print ('json error end=======================================')
            except UnicodeDecodeError:
                print ('UNICODE error=======================================')
                print (data[16:])
                print ('UNICODE error=======================================')

if __name__ == '__main__':
    #room_id = 71084
    # 010101
    # room_id = 989474
    # 魔王127直播间
    room_id = 1011
    dmj = DMJBot(room_id)
    dmj._start()
