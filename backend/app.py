import cherrypy
import os
import json
import psycopg2
import datetime

class App(object):
    exposed = True

    def connect_to_db(self):
        connect_str = "dbname='ark_mytest' user='postgres' host='localhost' password='pass'"
        self.conn = psycopg2.connect(connect_str)
        self.cursor = self.conn.cursor()

    def __init__(self):
        self.connect_to_db()

    def get_campaign_worker(self, key):
        self.cursor.execute("select * from campaigns where key='%s';" %(key))
        rows = self.cursor.fetchall()
        if len(rows)==0:
            return {}
	row = rows[0]        
        return {"vendorField": row[0],"name": row[1],"description": row[2],"goal": row[3],"created_on": row[4].strftime('%m-%d-%Y %H:%M:%S')}


    @cherrypy.tools.allow(methods=['POST','GET'])
    @cherrypy.expose
    def get_campaign(self, key):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        try:
            campaign = self.get_campaign_worker(key)
        except:
            self.connect_to_db()
            campaign = self.get_campaign_worker(key)
        return json.dumps(campaign)


    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.expose
    def create_campaign(self, key, name, description, goal):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        try:
            self.cursor.execute("insert into campaigns(key,name,description,goal,created_on) values ('%s', '%s', '%s', %s, current_timestamp);" %(key.replace("'","''"),name.replace("'","''"),description.replace("'","''"),goal))
            self.conn.commit()
        except:
            self.connect_to_db()
            self.cursor.execute("insert into campaigns(key,name,description,goal,created_on) values ('%s', '%s', '%s', %s, current_timestamp);" %(key.replace("'","''"),name.replace("'","''"),description.replace("'","''"),goal))
            self.conn.commit()
        return "success"


if __name__ == '__main__':
    #cherrypy.config.update({'server.socket_host': 'localhost', 'server.socket_port': 8084,'server.thread_pool' = 30 })
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8857
    #cherrypy.quickstart(App(), '/', "app.conf")
    cherrypy.quickstart(App())
