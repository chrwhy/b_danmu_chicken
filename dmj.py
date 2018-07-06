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

mutex = threading.Lock()
DANMAKUs = []
TO_ENGINE=False


def debug(msg):
    print(msg)
    
def info(msg):
    print(msg)

def warn(msg):
    print(msg)
    
def error(msg):
    print(msg)

def syn_danmu_msg(msg):
    if TO_ENGINE:
        mutex.acquire()
        DANMAKUs.append(msg)
        mutex.release()

def _tcp_start():
    print('Engine thread starting')
    serverName = '127.0.0.1'
    serverPort = 8080
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    while True:
        try:
            clientSocket.connect((serverName,serverPort))    
            break
        except ConnectionRefusedError:
            print('Engine side may not running, please check!!')
            continue

    while True:
        mutex.acquire()
        held_lock=True
        if len(DANMAKUs)>0:
            try:
                clientSocket.send(DANMAKUs[0].encode())
                del DANMAKUs[0]
                modifiedSentence = clientSocket.recv(512)
                print('From Server:', modifiedSentence.decode())
            except ConnectionResetError:            
                mutex.release()
                held_lock=False
                print('pipe broken, trying to re-connect')                
                while True:
                    try:
                        clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        clientSocket.connect((serverName,serverPort))    
                        break
                    except ConnectionRefusedError:
                        print('pipe broken, trying to re-connect')
                        time.sleep(1)
                        continue
        if held_lock:
            mutex.release()
        time.sleep(0.03)
    clientSocket.close()

def _heartbeat(self):
    while True:
        time.sleep(30)
        #xx = struct.pack('!IHHII', length, magic_num, version, msg_type, data_exchange_pack)
        heartbeat_pack = struct.pack('!IHHII', 16, 16, 1, 2, 1)        
        self.socket_client.send(heartbeat_pack + "".encode('utf-8'))
        print('❤❤❤❤❤❤❤❤❤❤❤\n')
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
        
        

        left=0
        last_package=''
        f = open('test1.txt', 'a+', 1, encoding='utf-8')
        while True:
            if left>0:
                print('❀❀❀❀❀❀❀❀❀❀ concate case ❀❀❀❀❀❀❀❀❀❀')
                current_package=self.socket_client.recv(left)
                print('☘☘left: ' + str(left))
                #print('☘☘last_package: \n' + last_package+'\n')
                #print(current_package)#encoded bytes
                #rint('☘☘current_package: \n' + current_package.decode('utf-8')+'\n')				
                #complete_msg=last_package+current_package[0:(len(current_package))].decode('utf-8')                
                try:
                    complete_msg=(last_package + current_package).decode('utf-8')
                except UnicodeDecodeError:
                    print('**************************')
                    print('concate msg decode error')
                    print(last_package + current_package)
                    print('**************************')
                f.write(complete_msg)
                f.write('\n')
                syn_danmu_msg(complete_msg)
                
                print('☘☘complete_msglete_msg: \n' + complete_msg)				
                print('❀❀❀❀❀❀❀❀❀❀ concate case ❀❀❀❀❀❀❀❀❀❀\n\n')
                left=0
                continue

            pre_data = self.socket_client.recv(16)
            print('☘☘pre_data length: ' + str(len(pre_data)))
            if len(pre_data) < 16:
                print('pre_data length less than 2...')                
                continue
				
            try:
                claimed_len, magic, ver, message_type, package_type = struct.unpack('!IHHII', pre_data)
                if claimed_len < 1:
                    print('***************************')
                    print('***************************')
                    print('***************************')
                    print('***************************')
                    continue
            except struct.error:
                print ('pre_data: ' + pre_data.decode('utf-8'))
                print ('pre_data_len: ' + str(len(pre_data)))
            if(claimed_len == 16):
                print ('Only control string received, skip it...')
                print (claimed_len)
                continue
            try:
                print('☘☘claimed length: ' + str(claimed_len))
                if claimed_len<16:
                    print('☘☘claimed length is too small')
                    continue
                if claimed_len>2000 and left==0:
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('Unknown package, looks like last package was lost ????!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!')
                    continue

                danmu_msg_package = self.socket_client.recv(claimed_len-16)                                
                if len(danmu_msg_package) == 0:
                    continue
                actual_len=len(danmu_msg_package)
                if actual_len<10 and claimed_len<=(actual_len+16):
                    print('actual length is too small ' + str(actual_len))
                    continue
                
                print('☘☘actual length: ' + str(actual_len))
                if claimed_len>(actual_len+16):
                    left=claimed_len-(actual_len+16)
                    try:
                        last_package=danmu_msg_package
                        print('☘☘' + str(left)+' bytes left, coming...')
                        continue
                    except UnicodeDecodeError:
                        print('UnicodeDecodeError***************************')
                        print(danmu_msg_package)
                        print('UnicodeDecodeError***************************\n\n')
                        continue
                danmu_msg_json = danmu_msg_package.decode('utf-8')
                print('☘☘Json format☘☘')
                print(danmu_msg_json)
                print('\n\n')
                #json_data = simplejson.loads(danmu_msg_json)
                #check json format only
                simplejson.loads(danmu_msg_json)
                f.write(danmu_msg_json)
                f.write('\n')
                syn_danmu_msg(danmu_msg_json)
            except simplejson.JSONDecodeError:
                print ('json error: ' + danmu_msg_json + '\n\n')                
            except UnicodeDecodeError:
                print ('UNICODE error: ' + danmu_msg)
                

if __name__ == '__main__':
    #room_id = 71084
    # 010101
    # room_id = 989474
    # 魔王127直播间
    room_id = 7734200
    dmj = DMJBot(room_id)    
    dmj._start()
