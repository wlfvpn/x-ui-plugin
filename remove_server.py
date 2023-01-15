import requests
from utils import load_config
from sqlitedb import SQLiteDB
from server import Server
from datetime import datetime
import random
import sqlite3

server='earth.womanlifefreedom.vip'

con = sqlite3.connect("database.db")
cur = con.cursor()
res = cur.execute(f"DELETE FROM users WHERE server='{server}';")
res.fetchall()
con.commit()
res = cur.execute(f"DELETE FROM inbounds WHERE server='{server}';")
res.fetchall()
con.commit()
con.close()