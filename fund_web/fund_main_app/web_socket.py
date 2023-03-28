# -*- coding: utf-8 -*-
import socket
import rsa
import pickle

def main(data):
    pubkey, privkey = rsa.newkeys(512)
    pubkey_by = pickle.dumps(pubkey)
    ip = "127.0.0.1"
    port = 4499
    ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ss.connect((ip,port))
    ss.send(pubkey_by)
    se_pubkey = ss.recv(1024)
    se_pubkey = pickle.loads(se_pubkey)
    data = rsa.encrypt(data.encode("utf-8"),se_pubkey)
    ss.send(data)
    data = ss.recv(1024)
    data = rsa.decrypt(data, privkey).decode("utf-8")
    print(data)
    ss.close()

if __name__ == "__main__":
    main("reboot")