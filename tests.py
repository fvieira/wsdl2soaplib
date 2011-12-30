# -*- coding: utf-8 -*-
import os
import sys
import unittest

import multiprocessing

import suds
import soaplib
import wsdl2soaplib

from wsgiref.simple_server import make_server
from soaplib.core.server import wsgi

# Simple wsdl file. Based on soaplib-server output for http://soaplib.github.com/soaplib/2_0/pages/helloworld.html
WSDL_CONTENT = """<?xml version='1.0' encoding='UTF-8'?>
<wsdl:definitions xmlns:wsa="http://schemas.xmlsoap.org/ws/2003/03/addressing" xmlns:tns="tns" xmlns:plink="http://schemas.xmlsoap.org/ws/2003/05/partner-link/" xmlns:xop="http://www.w3.org/2004/08/xop/include" xmlns:senc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s12env="http://www.w3.org/2003/05/soap-envelope/" xmlns:s12enc="http://www.w3.org/2003/05/soap-encoding/" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" targetNamespace="tns" name="Application">
    <wsdl:types>
        <xs:schema targetNamespace="tns" elementFormDefault="qualified">
            <xs:import namespace="http://www.w3.org/2001/XMLSchema" />
            <xs:complexType name="say_hello">
                <xs:sequence>
                    <xs:element name="name" type="xs:string" minOccurs="0" nillable="true" />
                    <xs:element name="times" type="xs:integer" minOccurs="0" nillable="true" />
                    <xs:element name="form" type="helloForms" minOccurs="0" nillable="true" />
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="stringArray">
                <xs:sequence>
                    <xs:element name="string" type="xs:string" minOccurs="0" maxOccurs="unbounded" nillable="true" />
                </xs:sequence>
            </xs:complexType>
            <xs:complexType name="say_helloResponse">
                <xs:sequence>
                    <xs:element name="say_helloResult" type="tns:stringArray" minOccurs="0" nillable="true" />
                </xs:sequence>
            </xs:complexType>
            <xs:simpleType name="helloForms">
                <xs:restriction base="xs:string">
                    <xs:enumeration value="Hello"/>
                    <xs:enumeration value="Good Day"/>
                    <xs:enumeration value="Hi"/>
                </xs:restriction>
            </xs:simpleType>
            <xs:element name="say_hello" type="tns:say_hello" />
            <xs:element name="stringArray" type="tns:stringArray" />
            <xs:element name="say_helloResponse" type="tns:say_helloResponse" />
        </xs:schema>
    </wsdl:types>
    <wsdl:message name="say_hello">
        <wsdl:part name="say_hello" element="tns:say_hello" />
    </wsdl:message>
    <wsdl:message name="say_helloResponse">
        <wsdl:part name="say_helloResponse" element="tns:say_helloResponse" />
    </wsdl:message>
    <wsdl:portType name="Application">
        <wsdl:operation name="say_hello" parameterOrder="say_hello">
            <wsdl:input name="say_hello" message="tns:say_hello" />
            <wsdl:output name="say_helloResponse" message="tns:say_helloResponse" />
        </wsdl:operation>
    </wsdl:portType>
    <wsdl:binding name="Application" type="tns:Application">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http" />
        <wsdl:operation name="say_hello">
            <soap:operation soapAction="say_hello" style="document" />
            <wsdl:input name="say_hello">
                <soap:body use="literal" />
            </wsdl:input>
            <wsdl:output name="say_helloResponse">
                <soap:body use="literal" />
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    <wsdl:service name="Application">
        <wsdl:port name="Application" binding="tns:Application">
            <soap:address location="http://localhost:9000/?wsdl" />
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""

class MainTestCase(unittest.TestCase):
    
    def setUp(self):
        wsdl = open("wsdl2soaplib_test.wsdl", "w")
        wsdl.write(WSDL_CONTENT)
        wsdl.close()
        
        #http://www.w3.org/2001/XMLSchema is regulary isnot available. 
        #We will load it from local file 
        suds.xsd.sxbasic.Import.bind('http://www.w3.org/2001/XMLSchema',
                    'file://' + os.path.abspath('cache/XMLSchema.xsd'))

    def tearDown(self):

        try:
            os.remove("wsdl2soaplib_test.wsdl")
        except OSError:
            pass

        try:
            os.remove("wsdl2soaplib_test.py")
            os.remove("wsdl2soaplib_test.pyc")
        except OSError:
            pass
    
    def testSimpleWSDL(self):
        
        client_for_generator = suds.client.Client("file://"+os.path.abspath("wsdl2soaplib_test.wsdl"))
        code = wsdl2soaplib.generate(client_for_generator, "wsdl2soaplib_test.wsdl")
        py = open("wsdl2soaplib_test.py", "w")
        py.write(code)
        py.close()
        
        from wsdl2soaplib_test import Application as HelloWorldService

        soap_application = soaplib.core.Application([HelloWorldService], 'tns')
        wsgi_application = wsgi.Application(soap_application)
        server = make_server('localhost', 9000, wsgi_application)
        
        soap_server = multiprocessing.Process(target=server.serve_forever)
        soap_server.start()
        
        client = suds.client.Client("http://localhost:9000/?wsdl")
        
        self.assertEqual(client.service.say_hello(), None)
        with self.assertRaises(Exception):
            client.service.undefined_method()
        
        soap_server.terminate()

if __name__ == '__main__':
    unittest.main()