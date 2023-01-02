import requests
from utils import load_config
from sqlitedb import SQLiteDB
from server import Server
from datetime import datetime
import random
import sqlite3

telegram_username='WomanLifeFreedomVPNSupport'
remark = '5861885059@WomanLifeFreedomVPNSupport'


con = sqlite3.connect("database.db")
cur = con.cursor()
res = cur.execute(f"DELETE FROM users WHERE telegram_username='{telegram_username}';")
res.fetchall()
con.commit()
con.close()

con = sqlite3.connect("/etc/x-ui/x-ui.db")
cur = con.cursor()
res = cur.execute(f"DELETE FROM inbounds WHERE remark='{remark}';")
res.fetchall()
con.commit()
con.close()
