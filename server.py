import requests
import uuid
import random
import json
from user import gen_user_config_vless_xtls,gen_user_config_vless_ws
from utils import load_config
from sqlitedb import SQLiteDB
from datetime import datetime

class Server():
    def __init__(self, address, max_users, username, password, port, traffic_limit, description, db, mode):
        self.address = address
        self.max_users = max_users
        self.username = username
        self.password = password
        self.port = port
        self.traffic_limit = traffic_limit
        self.db = db
        self.description = description
        self.mode = "SAME_PORT"
        self.vless_ws_port = 2053
        if self.mode=="SAME_PORT":
            self.initialize_inbound()
        print(f"Server {self.address} initialized successfully.")
            
    def login(self):
        payload = {'username': self.username, 'password': self.password}
        url = f"http://{self.address}:{self.port}/login" #TODO: Make it with https
        r = requests.post(url, data=payload)
        return r
    
    def initialize_inbound(self):
        remark = "vless-ws-tls-cdn"
        print('&&&&',self.db.query_from_remark_and_server('id',self.address,remark) )
        if self.db.query_from_remark_and_server('id',self.address,remark) is not None:
            return
        random_client_id =  str(uuid.uuid4()) 

        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_config = gen_user_config_vless_ws(name=remark, email="initialize@womanlifefreedom", uuid=random_client_id, server_address=self.address, port=2053, traffic_limit=self.traffic_limit)
        r = self.login()
        r = requests.post(f"http://{self.address}:{self.port}/xui/inbound/add", data=user_config, cookies=r.cookies) #TODO: Make it with http
        self.db.add_row('inbounds',(r.json()['obj']['id'],remark, r.json()['obj']['settings'], self.address, self.vless_ws_port, 0, creation_date))

    def get_load(self):
        return 0
    
    def generate_url(self, telegram_id, telegram_username, mode="SAME_PORT") -> tuple[bool,str]:
        if mode=="SAME_PORT":
            remark = telegram_id + '@' + telegram_username
            inbound_name = "vless-ws-tls-cdn"
            random_client_id =  str(uuid.uuid4())
            current_setting = self.db.query_from_remark_and_server('settings',self.address,inbound_name)
            clients = json.loads(current_setting)['clients']
            email = remark 
            config = gen_user_config_vless_ws(name=inbound_name, email=email, uuid=random_client_id, server_address=self.address, port=self.vless_ws_port, traffic_limit=self.traffic_limit, clients=clients)
            # print(config)
            inbound_id = self.db.query_from_remark_and_server('id',self.address,inbound_name)
            r = self.login()
            r = requests.post(f"http://{self.address}:{self.port}/xui/inbound/update/{inbound_id}", data=config, cookies=r.cookies) #TODO: Make it with https
            if json.loads(r.text)['success']:
                self.db.update_settings(inbound_id,config['settings'])
                creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                link = f"vless://{random_client_id}@66.235.200.136:{self.vless_ws_port}?type=ws&security=tls&host={self.address}&sni={self.address}&alpn=http/1.1&path=/wlf?ed=2048#WomanLifeFreedomVPN@{telegram_username}"
                self.db.add_row('users',(telegram_id, telegram_username, remark, random_client_id, creation_date, link, self.address, self.vless_ws_port))
                print(link)
                return True, link
            else:
                return False, None
                 
        elif mode=="SEPERATE_PORT":
            if traffic_limit is None:
                traffic_limit=self.traffic_limit
            random_client_id =  str(uuid.uuid4()) 
            port = self.db.generate_random_port(self.address)
            if port is None:
                print('Error, cannot get any ports from', self.address) #TODO: use logging
                return False, None
            
            user_config = gen_user_config_vless_xtls(remark, random_client_id, self.address, port, traffic_limit)
            print('sending**************************')
            r = self.login()
            r = requests.post(f"http://{self.address}:{self.port}/xui/inbound/add", data=user_config, cookies=r.cookies) #TODO: Make it with https
            if json.loads(r.text)['success']:
            #   print('Added', remark, r.content)
                link = f"vless://{random_client_id}@{self.address}:{port}?type=tcp&security=xtls&flow=xtls-rprx-direct&sni={self.address}&alpn=h2,http/1.1#{remark}"
                print(link)
                return True, link
            else:
            #   print("Error:",r.content)
                return False, None
         
if __name__=="__main__":
    config = load_config('config_test.yaml')

    db = SQLiteDB('database.db')
    server_name, server_config = config['servers'].popitem()
    
    Server = Server(server_name, **server_config, db = db)
    Server.generate_url('123','test-gp')
