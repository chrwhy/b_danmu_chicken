# coding: utf-8
import random
import os
import io
import sys
import _thread
import threading
import time
import requests
import xml.dom.minidom
import struct
import simplejson
from const import BCommand
import socket
import parser

mutex = threading.Lock()
DANMAKUs = []
PRINT_JSON=False
DEBUG=False

TO_ENGINE=True
ENGINE_IP = '172.18.95.25'
ENGINE_PORT = 18090

def debug(msg):
    if DEBUG:
        print(msg)
    
def info(msg):
    print(msg)

def warn(msg):
    print(msg)
    
def error(msg):
    print(msg)

def syn_danmu_msg(msg):
    if msg=='':
        return
    if TO_ENGINE:
        mutex.acquire()
        DANMAKUs.append(msg)
        mutex.release()

def print_json(json_data):
    if PRINT_JSON:
        print('☘ ☘ Json format☘ ☘')
        print(json_data) 
        print('\n')

def _tcp_start():
    print('Engine thread starting')
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientSocket.settimeout(5)
    while True:
        try:
            clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            clientSocket.settimeout(5)
            clientSocket.connect((ENGINE_IP, ENGINE_PORT))
            break
        except (ConnectionRefusedError, TimeoutError):
        #except:
            print('Engine side may not running, please check!!')
            time.sleep(5)
            continue

    while True:
        mutex.acquire()
        held_lock=True
        if len(DANMAKUs)>0:
            try:
                clientSocket.send(DANMAKUs[0].encode())
                del DANMAKUs[0]
                ack = clientSocket.recv(256)
                print('From Server:' + ack.decode())
            except (TimeoutError, BrokenPipeError, ConnectionResetError):            
                mutex.release()
                held_lock=False
                print('pipe broken, trying to re-connect')                
                while True:
                    try:
                        clientSocket.connect((ENGINE_IP, ENGINE_PORT))
                        clientSocket.settimeout(5)
                        break
                    except (ConnectionRefusedError,ConnectionResetError,ConnectTimeoutError):
                    #except:
                        print('failed to connect, trying to re-connect')
                        time.sleep(5)
                        continue
        if held_lock:
            mutex.release()
        time.sleep(0.03)
    clientSocket.close()

def _heartbeat(self):
    while True:
        time.sleep(30)
        #heartbeat_pack = struct.pack('!IHHII', length, magic_num, version, msg_type, data_exchange_pack)
        heartbeat_pack = struct.pack('!IHHII', 16, 16, 1, 2, 1)        
        self.socket_client.send(heartbeat_pack + "".encode('utf-8'))
        print('❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤\n')
        #\u2665

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
        #self.dm_host = dm_server[0].firstChild.data
        self.dm_host = '120.92.112.150'

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

    
    def GetData(self, expect):
        data=self.socket_client.recv(expect)
        if (len(data)==expect):
            return data
        left=expect-len(data)
        while left>0:
            data+=self.socket_client.recv(left)
            left=expect-(len(data))
        return data  

    def _start(self):
        _thread.start_new_thread(_heartbeat, (self,))
        if TO_ENGINE:
            _thread.start_new_thread(_tcp_start, ())
        
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

        f = open('test1.txt', 'a+', 1, encoding='utf-8')
        while True:
            pre_data = self.GetData(16) 
            #print('☘ ☘ pre_data length: ' + str(len(pre_data)))
            if len(pre_data) != 16:
                print('pre_data length:' + str(len(pre_data)) + ', which is supposed to be 16...')                
                print('pre_data length:' + str(len(pre_data)) + ', which is supposed to be 16...')                
                print('pre_data length:' + str(len(pre_data)) + ', which is supposed to be 16...')                

            try:
                claimed_len, magic, ver, message_type, package_type = struct.unpack('!IHHII', pre_data)
                if (message_type !=5):
                    print('message type: ' + str(message_type))
                if (package_type !=0):
                    print('package_type: ' + str(package_type))
                if (claimed_len == 20):
                    print('Heartbeat from Bilibili')
                    danmu_msg_package = self.socket_client.recv(claimed_len-16)                                
                    online = struct.unpack('!l', danmu_msg_package)
                    print('人气值: '+ str(online) + '\n')
                    continue
                #if claimed_len < 1:
                #    warn('claimed length less than 1, please check!!')
                #    continue
            except struct.error:
                print ('pre_data: ' + pre_data.decode('utf-8'))
                print ('pre_data_len: ' + str(len(pre_data)))
            
            try:
                print('☘ ☘ claimed length: ' + str(claimed_len))
                if claimed_len<16:
                    warn('☘ ☘ claimed length is too small')
                    continue
                if claimed_len>2000:
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('Unknown package, looks like last package was lost ????!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    exit()
                
                danmu_msg_package = self.GetData((claimed_len-16))
                danmu_msg_json = danmu_msg_package.decode('utf-8')
                print_json(danmu_msg_json)
                json_data = simplejson.loads(danmu_msg_json)
                f.write(danmu_msg_json)
                f.write('\n')
                danmu_brief = parser.parse_danmu(danmu_msg_json)
                syn_danmu_msg(danmu_brief)
            except simplejson.JSONDecodeError:
                print('json error: ' + danmu_msg_json + '\n\n')
                #continue
            except UnicodeDecodeError:
                print('UnicodeDecodeError***************************')
                print(danmu_msg_package)               
                print('UnicodeDecodeError***************************\n\n')
                #continue

if __name__ == '__main__':
    #room_id = 71084
    # 010101
    # room_id = 989474
    # 魔王127直播间
    #room_id = 7734200
    room_id = 5279
    dmj = DMJBot(room_id)    
    dmj._start()
