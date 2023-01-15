import requests
from utils import load_config
from sqlitedb import SQLiteDB
from server import Server
from datetime import datetime
import random

class ServerManager():
    def __init__(self,database_path='database.db',config_path='config.yaml'):
        self.config = load_config(config_path)
        self.servers = []
        self.db = SQLiteDB(database_path)
        for pool in self.config['pools'].keys(): 
            servers_in_a_pool = {}
            for server_addr, server_config in self.config['pools'][pool].items():
                servers_in_a_pool[server_addr] = Server(server_addr,**server_config, db=self.db)
            self.servers.append(servers_in_a_pool)
           
    def get_low_load_servers(self)-> Server:
        # return min(self.servers.values(), key=lambda s: s.get_load())
        low_load_servers = []
        for pool in self.servers:
            low_load_servers_in_a_pool = []
            for server_address, server in pool.items():
                if self.db.count_entries_for_server(server=server_address)<=server.max_users:
                    low_load_servers_in_a_pool.append(server)
            low_load_servers.append(low_load_servers_in_a_pool)
        if not low_load_servers:
            return None
        
        output = []
        for pool in low_load_servers:
            output.append(random.choice(pool))
        return output
 
       
    def generate_url(self, telegram_id, telegram_username):
        if self.config['generate_unique']:
            existing_links_and_servers_desc = self.db.get_links_and_server_desc(telegram_id)
            # existing_server = self.db.get_server(telegram_id)
            if existing_links_and_servers_desc is not None:
                return  existing_links_and_servers_desc            
        servers = self.get_low_load_servers()
        if servers is None:
            print('Error: server is full.')
            return False, 'سرور در حال حاضر پر می باشد. لطفا بعدا مجدد تلاش کنید...'
        output = []
        remark = telegram_id + '@' + telegram_username
        for server in servers:
            ret, link = server.generate_url(telegram_id,telegram_username)
            if ret:
                output.append({'desc':server.description,'url':link})
            else:
                print(f'Error: Cannot generate link for {telegram_username} from {server.address}')
                output.append({'desc':f"Error! Could not generate link for {server.address}",'url':None})
        
        return output
    
if __name__=="__main__":
  ServerManager= ServerManager('test.db')
  ServerManager.generate_url('211','server_manager_test')
