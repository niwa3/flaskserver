# -*- coding: utf-8 -*-
import sys
from time import sleep
import xml.etree.ElementTree as ET
import socket
from flask import Flask, request, render_template, redirect, url_for, make_response, session, escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hYFfHpuw1QzwfbkrqwCrNDtJ9vTsSo'
SOCK_FILENAME = '/tmp/unix-socket'

class Client:
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def SendXML(self, source):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket_path)
        size = len(source)
        sys.stdout.write("{} \n".format(str(size)))
        if(s.send(str(size).encode('utf-8'))):
            sleep(0.01)
            if(s.send(source)):
                sleep(0.01)
        s.close()

    def GetXml(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket_path)
        size=s.recv(16)
        if(size>0):
            sys.stdout.write(size)
            source=s.recv(int(size))
        s.close()
        return str(source)




class XmlCreate:
    def __init__(self):
        self.transport=ET.Element("transport")
        self.header=ET.SubElement(self.transport,"header")
        self.body=ET.SubElement(self.transport,"body")

    def auth(self, u, p):
        method=ET.SubElement(self.header, "method")
        method.text = "authentication"
        auth_info=ET.SubElement(self.body, "auth_info")
        username=ET.SubElement(auth_info, "username")
        username.text = u
        password=ET.SubElement(auth_info, "password")
        password.text = p
        return ET.tostring(self.transport, 'utf-8')

class XmlParse:
    def __init__(self, source):
        self.transport=ET.fromstring(source)
        self.header=transport.find(".//header")
        self.body=transport.find(".//body")

    def header(self):
        method=self.header.find(".//method")
        return method.text

    def userid(self):
        userid=self.body.find(".//userid")
        return userid.text




@app.before_request
def before_request():
    if session.get('userid') is not None:
        if request.path == '/login' or request.path == '/':
            return redirect(url_for('welcome'))
        return
    if request.path == '/login':
        return
    if request.path == '/':
        return
    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST' and _is_account_valid():
        sys.stdout.write("auth")
        xmlcreate = XmlCreate()
        client = Client(SOCK_FILENAME)
        client.SendXML(xmlcreate.auth(request.form['username'], request.form['password']))
        xmlparse = XmlParse(client.GetXml())
        userid = xmlparse.userid()
        if(userid is not None):
            session['userid'] = userid
            return redirect(url_for('welcome'))
        else:
            error = 'error'
    return render_template('login.html', error = error)

#def _do_the_login(userid):
#    sys.stdout.write("auth")
#    xmlcreate = XmlCreate()
#    client = Client(FILENAME)
#    Client.SendXML(xmlcreate.auth(request.form['username'], request.form['password']))
#    xmlparse = XmlParse(Client.GetXml())
#    userid = xmlparse.userid()
#    return True

def _is_account_valid():
    if request.form['username'] is None:
        return False
    return True

@app.route('/welcome', methods=['GET'])
def welcome():
    return render_template('index.html')
#    if 'session_id' in session:
#    return render_template('layout.html')
#    return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
