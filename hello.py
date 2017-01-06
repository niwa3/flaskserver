# -*- coding: utf-8 -*-
import sys
#from OpenSSL import SSL
from struct import *
from time import sleep
import xml.etree.ElementTree as ET
import socket
from flask import Flask, request, render_template, redirect, url_for, make_response, session, escape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hYFfHpuw1QzwfbkrqwCrNDtJ9vTsSo'
SOCK_FILENAME = '/tmp/unix-socket'
#context = SSL.Context(SSL.TLSv1_METHOD)
#context.use_privatekey_file('server.key')
#context.use_certificate_file('server.crt')

class Client:
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def Create(self):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.connect(self.socket_path)

    def SendXML(self, source):
        size = len(source)
        if(self.s.send(pack('i',size))):
            sleep(0.01)
            if(self.s.send(source)):
                sleep(0.01)

    def GetXml(self):
        row_size=unpack('i',self.s.recv(4))
        size=row_size[0]
        if(int(size)>0):
            source=self.s.recv(int(size)).decode()
        return str(source)

    def Close(self):
        self.s.close()




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

    def newnode(self, nid, uid, plvl, ntype, dtype, inter, loca):
        method=ET.SubElement(self.header, "method")
        method.text = "register_newnode"
        node=ET.SubElement(self.body, "node")
        nodeid=ET.SubElement(node, "nodeid")
        userid=ET.SubElement(node, "userid")
        privacy_lvl=ET.SubElement(node, "privacy_lvl")
        node_type=ET.SubElement(node, "node_type")
        data_type=ET.SubElement(node, "data_type")
        interval=ET.SubElement(node, "interval")
        location=ET.SubElement(node, "location")
        nodeid.text = nid
        userid.text = uid
        privacy_lvl.text =plvl
        node_type.text = ntype
        data_type.text = dtype
        interval.text = inter
        location.text = loca
        return ET.tostring(self.transport, 'utf-8')

    def newservice(self, sid, vid, plvl, dtype, inter):
        method=ET.SubElement(self.header, "method")
        method.text = "register_newservice"
        service=ET.SubElement(self.body, "service")
        serviceid=ET.SubElement(service, "serviceid")
        venderid=ET.SubElement(service, "venderid")
        privacy_lvl=ET.SubElement(service, "privacy_lvl")
        data_type=ET.SubElement(service, "data_type")
        interval=ET.SubElement(service, "interval")
        serviceid.text = sid
        venderid.text = vid
        privacy_lvl.text =plvl
        data_type.text = dtype
        interval.text = inter
        return ET.tostring(self.transport, 'utf-8')

    def changeprivacy(self, sid, nid, plvl):
        method=ET.SubElement(self.header, "method")
        method.text = "privacy"
        privacy=ET.SubElement(self.body, "privacy")
        serviceid=ET.SubElement(privacy, "serviceid")
        nodeid=ET.SubElement(privacy, "nodeid")
        privacy_lvl=ET.SubElement(privacy, "privacy_lvl")
        serviceid.text = sid
        nodeid.text = nid
        privacy_lvl.text =plvl
        return ET.tostring(self.transport, 'utf-8')



class XmlParse:
    def __init__(self, source):
        self.transport=ET.fromstring(source)
        self.header=self.transport.find(".//header")
        self.body=self.transport.find(".//body")

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
            return redirect(url_for('home'))
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
        xmlcreate = XmlCreate()
        client = Client(SOCK_FILENAME)
        client.Create()
        client.SendXML(xmlcreate.auth(request.form['username'], request.form['password']))
        xmlparse = XmlParse(client.GetXml())
        client.Close()
        userid = xmlparse.userid()
        if(userid is not None):
            session['userid'] = userid
            return redirect(url_for('home'))
        else:
            error = 'error'
    return render_template('login.html', error = error)


def _is_account_valid():
    if request.form['username'] is None:
        return False
    return True

@app.route('/home', methods=['GET'])
def home():
    if(session.get("userid") is None):
        return redirect(url_for('login'))
    return render_template('home.html', userid = session.get("userid"))

@app.route('/home/newnode', methods=['GET','POST'])
def register_new_node():
    if request.method == 'POST':
        xmlcreate = XmlCreate()
        client = Client(SOCK_FILENAME)
        client.Create()
        client.SendXML(xmlcreate.newnode(request.form['nodeid'], request.form['userid'], request.form['privacy_lvl'], request.form['node_type'], request.form['data_type'], str(request.form['interval']), request.form['location']))
        client.Close()
    return render_template('newnode.html', userid = session.get("userid"))

@app.route('/home/newservice', methods=['GET','POST'])
def register_new_service():
    if request.method == 'POST':
        xmlcreate = XmlCreate()
        client = Client(SOCK_FILENAME)
        client.Create()
        client.SendXML(xmlcreate.newservice(request.form['serviceid'], request.form['venderid'], request.form['privacy_lvl'], request.form['data_type'], str(request.form['interval'])))
        client.Close()
    return render_template('newservice.html', userid = session.get("userid"))

@app.route('/home/relation',methods=['GET','POST'])
def change_privacy_lvl():
    if request.method == 'POST':
        xmlcreate = XmlCreate()
        client = Client(SOCK_FILENAME)
        client.Create()
        client.SendXML(xmlcreate.changeprivacy(request.form['serviceid'], request.form['nodeid'], request.form['privacy_lvl']))
        client.Close()
    return render_template('relation.html', userid = session.get("userid"))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    context = ('server.crt','server.key')
    app.run(debug=True, ssl_context=context)
