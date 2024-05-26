from flask import Flask
import requests
import threading
import time
from werkzeug.serving import make_server
import json
from pathlib import Path
from datetime import date, datetime, timedelta
from flask_cors import CORS, cross_origin
# import os
# port = os.environ["PORT"]
global server
global running
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
script_location = Path(__file__).absolute().parent

class ServerThread(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 10000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

@app.route("/")
def home():
        print(timedelta(0,5))
        return "Hello!"

@app.route("/list")
def getList():
      file_location = script_location / "data.json"
      f = file_location.open()
      data = json.load(f)
      f.close()
      file_location = script_location / "websites.json"
      f = file_location.open()
      siteList = json.load(f)
      f.close()
      return data
    #   for site in siteList["list"]:
            


@app.route("/shutdown")
def close_server():
      global running
      running = False
      server.shutdown()

def serialize_timedelta(obj):
    if isinstance(obj, timedelta):
        return {"days": obj.days, "seconds": obj.seconds, "microseconds": obj.microseconds}
    raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")

def pingServers():
        while running:
                try:
                    file_location = script_location / "data.json"
                    f = file_location.open()
                    data = json.load(f)
                    f.close()
                    file_location = script_location / "websites.json"
                    f = file_location.open()
                    siteList = json.load(f)
                    f.close()
                    # print(siteList["list"])
                    for site in siteList["list"]:
                        response = requests.get(f"http://{site}",timeout = 5)
                        if(response.ok):
                                print(response.elapsed)
                                print(response.url)
                                data[site].insert(0,response.elapsed)
                                if len(data[site]) > 50:
                                    data[site].pop(50)
                except:
                    print("error! Maybe request didnt make it")
                    data[site].insert(0,timedelta(0,5))
                    if len(data[site]) > 50:
                        data[site].pop(50)

                file_location = script_location / "data.json"
                f = file_location.open("w")
                f.write(json.dumps(data, default=serialize_timedelta))
                f.close()
                
                time.sleep(10)




if __name__ == "__main__":
        server = ServerThread(app)
        server.start()
        running = True
        file_location = script_location / "websites.json"
        f = file_location.open()
        siteList = json.load(f)
        f.close()
        file_location = script_location / "data.json"
        f = file_location.open("w")
        obj = {}
        for site in siteList["list"]:
              obj[site] = []
        f.write(json.dumps(obj))
        f.close()
        serverThread = threading.Thread(target=app.run)
        serverThread.start()
        pingingThread = threading.Thread(target=pingServers)
        pingingThread.start()

