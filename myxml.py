import xml.etree.ElementTree as ET

class XmlCreate:
    def __init__(self):
        self.header=ET.Element("header")
        self.body=ET.Element("body")

    def auth(self, u, p):
        method=ET.SubElement(self.header, "method")
        method.text = "authentication"
        username=ET.SubElement(self.body, "username")
        username.text = u
        password=ET.SubElement(self.body, "password")
        password.text = p
