import requests
import uuid
import random
import json
from user import gen_user_config
from utils import load_config
from sqlitedb import SQLiteDB


class Server():
    def __init__(self, address, max_users, username, password, port, traffic_limit, db):
        self.address = address
        self.max_users = max_users
        self.username = username
        self.password = password
        self.port = port
        self.traffic_limit = traffic_limit
        self.db = db
    
    def login(self):
        payload = {'username': self.username, 'password': self.password}
        url = f"http://{self.address}:{self.port}/login" #TODO: Make it with https
        r = requests.post(url, data=payload)
        return r
        
    def get_load(self):
        return 0
    
    def generate_url(self, remark:str, traffic_limit:int=None) -> tuple[bool,str]:
        if traffic_limit is None:
            traffic_limit=self.traffic_limit
        random_client_id =  str(uuid.uuid4()) 
        port = self.db.generate_random_port(self.address)
        if port is None:
            print('Error, cannot get any ports from', self.address) #TODO: use logging
            return False, None, None
        
        user_config = gen_user_config(remark, random_client_id, self.address, port, traffic_limit)
        
        r = self.login()
        r = requests.post(f"http://{self.address}:{self.port}/xui/inbound/add", data=user_config, cookies=r.cookies) #TODO: Make it with https
        if json.loads(r.text)['success']:
          print('Added', remark, r.content)
          link = f"vless://{random_client_id}@{self.address}:{port}?type=tcp&security=xtls&flow=xtls-rprx-direct&sni={self.address}&alpn=h2,http/1.1#{remark}"
          print(link)
          return True, link, port
        else:
          print("Error:",r.content)
          return False, None, None
          
if __name__=="__main__":
    config = load_config()
    db = SQLiteDB('database.db')
    server_name, server_config = config['servers'].popitem()
    
    Server = Server(server_name, **server_config, db = db)
    Server.generate_url('vless@test-gp')
