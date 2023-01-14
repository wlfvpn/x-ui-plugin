import requests
import uuid
import random
import json
from user import gen_user_config_vless_xtls,gen_user_config_vless_ws
from utils import load_config
from sqlitedb import SQLiteDB
from datetime import datetime

class Server():
    def __init__(self, address, max_users, username, password, port, traffic_limit, description, same_port, multi_port, cdn, ip, db):
        self.address = address
        self.max_users = max_users
        self.username = username
        self.password = password
        self.port = port
        self.traffic_limit = traffic_limit
        self.db = db
        self.description = description
        self.same_port = same_port
        self.multi_port = multi_port
        self.cdn = cdn
        self.ip = ip
        if self.same_port['active'] == self.multi_port['active']:
            raise Exception(f"Turn on either 'same_port' or 'multiport' for {self.address}.")
        
        if self.cdn and self.multi_port['active']:
            raise Exception(f"CDN and 'multi_port' cannot be ON at the same time for {self.address}.")

        cloudflare_http_ports = [80, 8080, 8880, 2052, 2082, 2086, 2095] 
        cloudflare_https_ports = [443, 2053, 2083, 2087, 2096, 8443]
        
        if self.cdn and self.port not in cloudflare_http_ports: #change to cloudflare_http_ports if you use https panel 
            self.url = f"{self.ip}:{self.port}"
        else:
            self.url = f"{self.address}:{self.port}"
            
        if self.same_port['active']:
            self.initialize_inbound()
            print('initialized inbound')
            
        print(f"Server {self.address} initialized successfully.")
            
    def login(self):
        payload = {'username': self.username, 'password': self.password}
        url = f"http://{self.url}/login" #TODO: Make it with https
        r = requests.post(url, data=payload)
        return r
    
    def initialize_inbound(self):
        remark = "vless-ws-tls-cdn"
        if self.db.query_from_remark_and_server('id',self.address,remark) is not None:
            return
        random_client_id =  str(uuid.uuid4()) 

        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_config = gen_user_config_vless_ws(name=remark, email="initialize@womanlifefreedom", uuid=random_client_id, server_address=self.address, port=self.same_port['port'], traffic_limit=self.traffic_limit)
        r = self.login()
        r = requests.post(f"http://{self.url}/xui/inbound/add", data=user_config, cookies=r.cookies) #TODO: Make it with http
        print(r)
        self.db.add_row('inbounds',(r.json()['obj']['id'],remark, r.json()['obj']['settings'], self.address, self.same_port['port'], 0, creation_date))

    def get_load(self):
        return 0

    def generate_url(self, telegram_id, telegram_username) -> tuple[bool,str]:
        random_client_id =  str(uuid.uuid4())
        remark = telegram_id + '@' + telegram_username
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        links = []
        
        
        if self.same_port['active']:
            inbound_name = "vless-ws-tls-cdn"
            # current_setting = self.db.query_from_remark_and_server('settings',self.address,inbound_name)
            # clients = json.loads(current_setting)['clients']
            clients = self.db.get_clients(self.address, self.traffic_limit)
            email = remark 
            config = gen_user_config_vless_ws(name=inbound_name, email=email, uuid=random_client_id, server_address=self.address, port=self.same_port['port'], traffic_limit=self.traffic_limit, clients=clients)
            # print(config)
            inbound_id = self.db.query_from_remark_and_server('id',self.address,inbound_name)
            r = self.login()
            r = requests.post(f"http://{self.url}/xui/inbound/update/{inbound_id}", data=config, cookies=r.cookies) #TODO: Make it with https
            result = json.loads(r.text)
            if result['success']:
                self.db.update_settings(inbound_id,result['obj']['settings'])
                
                link = f"vless://{random_client_id}@66.235.200.136:{self.same_port['port']}?type=ws&security=tls&host={self.address}&sni={self.address}&alpn=http/1.1&path=/wlf?ed=2048#WomanLifeFreedomVPN@{telegram_username}"
                self.db.add_row('users',(telegram_id, telegram_username, remark, random_client_id, creation_date, link, self.address, self.same_port['port'],'same_port',self.description))
                print(link)
                links.append(link)
            else:
                return False, None
                 
        if self.multi_port['active']:
            port = self.db.generate_random_port(self.address)
            if port is None:
                print('Error, cannot get any ports from', self.address) #TODO: use logging
                return False, None           
            user_config = gen_user_config_vless_xtls(remark, telegram_id, random_client_id, self.address, port, self.traffic_limit)
            r = self.login()
            r = requests.post(f"http://{self.url}/xui/inbound/add", data=user_config, cookies=r.cookies) #TODO: Make it with https
            if json.loads(r.text)['success']:
            #   print('Added', remark, r.content)
                if self.cdn:
                    print('ERROR: xtls is not supported in CDN mode.')
                link = f"vless://{random_client_id}@{self.address}:{port}?type=tcp&security=xtls&flow=xtls-rprx-direct&sni={self.address}&alpn=h2,http/1.1#{remark}"
                self.db.add_row('users',(telegram_id, telegram_username, remark, random_client_id, creation_date, link, self.address, port,'multi_port', self.description))

                print(link)
                links.append(link)
            else:
                print("Error:",r.content)
                return False, link[0]
            
        return True, '\n \n'.join(links)
         
if __name__=="__main__":
    config = load_config('config_test.yaml')

    db = SQLiteDB('database.db')
    server_name, server_config = config['servers'].popitem()
    
    Server = Server(server_name, **server_config, db = db)
    Server.generate_url('123','test-gp')
