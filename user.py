import requests
import uuid
import random
import json

def gen_user_config(name :str, my_uuid:str, server_address:str, port: int, traffic_limit=0):
  clients = {"clients": [
      {
        "id": my_uuid,
        "flow": "xtls-rprx-direct"
      }
    ],
    "decryption": "none",
    "fallbacks": []
  }

  streamsetting = {
    "network": "tcp",
    "security": "xtls",
    "xtlsSettings": {
      "serverName": server_address,
      "alpn": ["h2","http/1.1"],
      "certificates": [
        {
          "certificateFile": "/root/cert.crt",
          "keyFile": "/root/private.key"
        }
      ]
    },
    "tcpSettings": {
      "header": {
        "type": "none"
      }
    }
  }

  sniff_sett={
    "enabled": True,
    "destOverride": [
      "http",
      "tls"
    ]
  }
    
  data = {'up':0,
  'down':0,
  'total':traffic_limit,
  'remark':name,
  'enable':'true',
  'expiryTime':0,
  'listen':None,
  'port':port ,
  'protocol':"vless",
  'settings' : json.dumps(clients),
  'streamSettings':json.dumps(streamsetting),
  'sniffing':json.dumps(sniff_sett)
  }
  return data
