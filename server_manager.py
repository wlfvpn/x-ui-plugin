import requests
from utils import load_config
from sqlitedb import SQLiteDB
from server import Server
from datetime import datetime
import random

class ServerManager():
    def __init__(self,database_path='database.db',config_path='config.yaml'):
        self.config = load_config(config_path)
        self.servers = {}
        self.db = SQLiteDB(database_path)
        for server_addr, server_config in self.config['servers'].items():
            self.servers[server_addr] = Server(server_addr,**server_config, db=self.db)
    
    def get_low_load_server(self)-> Server:
        # return min(self.servers.values(), key=lambda s: s.get_load())
        low_load_servers = []
        
        for server_address, server in self.servers.items():
            if self.db.count_entries_for_server(server=server_address)<=server.max_users:
                low_load_servers.append(server)
        
        if not low_load_servers:
            return None
        
        return random.choice(low_load_servers)
 
       
    def generate_url(self, telegram_id, telegram_username):
        if self.config['generate_unique']:
            existing_links = self.db.get_links(telegram_id)
            existing_server = self.db.get_server(telegram_id)
            if existing_links is not None and existing_server is not None:
                return True, existing_links, self.servers[existing_server].description
                
        server = self.get_low_load_server()
        if server is None:
            print('Error: server is full.')
            return False, 'سرور در حال حاضر پر می باشد. لطفا بعدا مجدد تلاش کنید...'
        
        remark = telegram_id + '@' + telegram_username
        ret, link = server.generate_url(telegram_id,telegram_username)
        if ret:
            return True, link, server.description
        else:
            print(f'Error: Cannot generate link for {telegram_username} from {server.address}')
            return False, "Server couldn't generate a link. Please retry.", None
        
        
if __name__=="__main__":
  ServerManager= ServerManager('test.db')
  ServerManager.generate_url('211','server_manager_test')
