import requests
from utils import load_config
from sqlitedb import SQLiteDB
from server import Server
from datetime import datetime
import random
import sqlite3

telegram_username='mhmdreza_farokhi8'
remark = '5861885059@WomanLifeFreedomVPNSupport'

con = sqlite3.connect("database.db")
cur = con.cursor()
res = cur.execute(f"DELETE FROM users WHERE telegram_username='{telegram_username}';")
res.fetchall()
con.commit()
con.close()


#  then remove manually from x-ui fro that server



# con = sqlite3.connec
# t("/etc/x-ui/x-ui.db")
# cur = con.cursor()
# res = cur.execute(f"DELETE FROM inbounds WHERE remark='{remark}';")
# res.fetchall()
# con.commit()
# con.close()
