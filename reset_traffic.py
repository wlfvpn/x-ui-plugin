import sqlite3
con = sqlite3.connect("/etc/x-ui/x-ui.db")
cur = con.cursor()
res = cur.execute("UPDATE inbounds SET up=0, down=0, enable=1")
# res = cur.execute("UPDATE inbounds SET down=0 WHERE remark='test'")
# res = cur.execute("UPDATE inbounds SET enable=0 WHERE remark='test'")
res.fetchone()
con.commit()
con.close()
