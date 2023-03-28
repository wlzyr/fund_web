import webbrowser
import os
import time
import threading

def web():
    while(1):
        time.sleep(1)
        net = os.popen('netstat -ano |findstr "8000"').read()
        if net:
            webbrowser.open("http://127.0.0.1:8000/index/")
            break

def web_server():
    os.system(r"python manage.py runserver")

if __name__ == "__main__":
    th1 = threading.Thread(target=web_server)
    th2 = threading.Thread(target=web)
    th1.start()
    th2.start()
