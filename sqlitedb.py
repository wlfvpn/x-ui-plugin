import sqlite3
import random

class SQLiteDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connect()
        self.conn.row_factory = sqlite3.Row

        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not self.cursor.fetchone():
            self.cursor.execute(f"CREATE TABLE users (telegram_id, telegram_username, remark, uuid, creation_date, link, server, port, mode, server_desc)")
        
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='inbounds'")
        if not self.cursor.fetchone():
            self.cursor.execute(f"CREATE TABLE inbounds (id, remark, settings, server, port, max_limit, creation_date)")
    
    def update_settings(self, id, settings):
        # update the settings for the given id
        self.conn.execute("UPDATE inbounds SET settings = ? WHERE id = ?", (settings, id))

        # commit the changes and close the connection
        self.conn.commit()

    def get_inbound_id_from_remark_and_server(self, server, remark):
        """Count the number of entries with the given server in the given table"""
        query = f"SELECT id FROM inbounds WHERE server = ? AND remark = ?"
        self.cursor.execute(query, (server,remark))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None    
     
    def add_row(self, table_name, values):
        """Insert a row into the given table, creating the table if it does not exist"""
        placeholders = ", ".join("?" * len(values))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

        
        
    def count_entries_for_server(self, server):
        """Count the number of entries with the given server in the given table"""
        query = f"SELECT COUNT(*) FROM users WHERE server = ?"
        self.cursor.execute(query, (server,))
        row = self.cursor.fetchone()
        return row[0]  
      
    def query(self,table_name, requested_column, match_column_name,match_column_value ):
        query = f"SELECT ? FROM ? WHERE ? = ?"
        self.cursor.execute(query, (requested_column,table_name,match_column_name,match_column_value))
        rows = self.cursor.fetchone()
        if rows:
            return rows[0]
        return None
    
    def query_from_remark_and_server(self, column_name, server, remark):
        """Count the number of entries with the given server in the given table"""
        query = f"SELECT {column_name} FROM inbounds WHERE server = ? AND remark = ?"
        self.cursor.execute(query, (server,remark))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None  
          
    def get_clients(self, server,totalGB):
        # Select the columns you want to retrieve
        self.cursor.execute("SELECT remark, uuid FROM users WHERE server=?", (server,))

        # Fetch all rows as a list of tuples
        rows = self.cursor.fetchall()

        # Create an empty list to store the JSON objects
        json_list = []

        # Iterate through the rows
        for row in rows:
            json_list.append({'email': row[0], 'id': row[1], 'flow': 'xtls-rprx-direct', 'totalGB': totalGB})

        return json_list

    # def get_links_and_server(self, telegram_id):
    #         """Returns the link for the given telegram_id, or None if not found"""
    #         query = f"SELECT link, server FROM users WHERE telegram_id = ?"
    #         self.cursor.execute(query, (telegram_id,))
    #         rows = self.cursor.fetchall()
            
    #         if rows:
    #             return [{'url': row[0], 'server': row[1]} for row in rows]
    #         return None
        
    def get_links_and_server_desc(self, telegram_id):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT link, server_desc FROM users WHERE telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        rows = self.cursor.fetchall()
        if rows:
            result = []
            current_server = rows[0][1]
            current_urls = []
            for row in rows:
                if row[1] == current_server:
                    current_urls.append(row[0])
                else:
                    result.append({'desc': current_server, 'url': '\n \n'.join(current_urls)})
                    current_server = row[1]
                    current_urls = [row[0]]
            result.append({'desc': current_server, 'url': '\n \n'.join(current_urls)})
            return result
        return None

    def get_server(self, telegram_id):
        """Returns the link for the given telegram_id, or None if not found"""
        query = f"SELECT server FROM users WHERE telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        rows = self.cursor.fetchone()
        if rows:
            return rows[0]
        return None
    
    def generate_random_port(self, server):
        """Generates a random port that is not in the table for the given server"""
        port = random.randint(10000, 50000)
        query = f"SELECT ? WHERE NOT EXISTS (SELECT 1 FROM users WHERE server = ? AND port = ?)"
        self.cursor.execute(query, (port, server, port))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def remove_row(self, table_name, criteria):
        """Delete a row from the given table based on the given criteria, creating the table if it does not exist"""
        query = f"DELETE FROM {table_name} WHERE {criteria}"
        self.cursor.execute(query)
        self.conn.commit()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close the database connection"""
        self.conn.close()
        
    
    def __del__(self):
        self.cursor.close()
        self.conn.close()

if __name__=="__main__":
    db = SQLiteDB('database.db')
    # db.add_row('users',('my_id', 'my_username', 'my_id@my_username', '2022', 'vles://xyz', '127.0.0.1', '443', 0, '700000'))
    # print(db.generate_random_port('127.0.0.1'))
    print(db.get_settings('google.womanlifefreedom.vip',1000))
    db.close()