import requests
import uuid
import random
import json

def gen_user_config_vless_xtls(name :str,email, my_uuid:str, server_address:str, port: int, traffic_limit, clients=None):
  new_client = [
        {"email": email,
          "id": my_uuid,
          "flow": "xtls-rprx-direct",
        }]
  if clients:
    clients += new_client
  else:
    clients = new_client
     
  clients = {"clients": clients,
    "decryption": "none",
    "fallbacks": []
  }

  streamsetting = {
    "network": "tcp",
    "security": "xtls",
    "xtlsSettings": {
      "serverName": server_address,
      "alpn": "h2,http/1.1",
      "certificates": [
        {
          "certificateFile": "/root/cert.crt",
          "keyFile": "/root/private.key"
        }
      ]
    },
    "tcpSettings": {
      "acceptProxyProtocol": False,
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


def gen_user_config_vless_ws(name :str,email, uuid:str, server_address:str, port: int, traffic_limit=0,clients=None):
  new_client = [
        {"email": email,
          "id": uuid,
          "flow": "xtls-rprx-direct",
          "totalGB": traffic_limit

        }]
  if clients:
    clients += new_client
  else:
    clients = new_client
     
  clients = {"clients": clients,
    "decryption": "none",
    "fallbacks": []
  }

  streamsetting = {
    "network": "ws",
    "security": "tls",
    "tlsSettings": {
      "serverName": server_address,
      "alpn": ["http/1.1"],
      "certificates": [
        {
          "certificateFile": "/root/cert.crt",
          "keyFile": "/root/private.key"
        }
      ]
    },
    "wsSettings": {
      "acceptProxyProtocol": False,
      "path": "/wlf?ed=2048",
      "header": {
        "Host": "google.womanlifefreedom.vip",
        "headerType": "none"
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
  'total':0,
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
