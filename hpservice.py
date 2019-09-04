from pybleno import *
import array

to_Address=''
class SetToAddress(Characteristic):
    
    # control application to request the API by methods
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '1000',
            'properties': ['read','write'],
            'value': None }
            )
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        #type:payloads
        global to_Address
        print('encode: ',str(data.decode()))
        to_Address += str(data.decode())
        print('decode: ',to_Address)
        callback(Characteristic.RESULT_SUCCESS)
    
    def onReadRequest(self,offset,callback):
        global to_Address
        callback(Characteristic.RESULT_SUCCESS, to_Address.encode('utf8'))

transactions = ''
class SetTransaction(Characteristic):
    # control application to request the API by methods
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '1001',
            'properties': ['read','write'],
            'value': None }
        )
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        #type:payloads
        global transactions
        print('encode: ',str(data.decode()) )
        transactions += str(data.decode())
        print('decode: ',transactions)
        callback(Characteristic.RESULT_SUCCESS)
    
    def onReadRequest(self,offset,callback):
        global transactions
        callback(Characteristic.RESULT_SUCCESS, transactions.encode('utf8') )


uri = ''
class UriChrc(Characteristic):

    CHRC_UUID = '00002ab6-0000-1000-8000-00805f9b34fb'
    
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2AB6',
            'properties': ['write'],
            'value': None }
            )
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        value = str(data.decode())
        print('write uri: ',data)
        global uri
        uri = 'http://127.0.0.1:6000/'+value
        print('uri you write in:',uri)
        callback(Characteristic.RESULT_SUCCESS)
    def getUri(self):
        global uri
        print('you getUri :',uri)
        return uri

class HttpHeadersChrc(Characteristic):

    CHRC_UUID = '00002ab7-0000-1000-8000-00805f9b34fb'
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2AB7',
            'properties': ['notify'],
            'value': None }
            )
        self.http_headers = ""
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('EchoCharacteristic - onSubscribe')
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('EchoCharacteristic - onUnsubscribe');
        self._updateValueCallback = None

class HttpEntityBodyChrc(Characteristic):
    CHRC_UUID = '00002ab9-0000-1000-8000-00805f9b34fb'
    # put the response in to EnityBody
    body = dict()
    
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2AB9',
            'properties': ['read'],
            'value': None }
            )
        
    def set_http_entity_body(self,value):
        print('body value you set: ',value)
        self.body = value
    
    def onReadRequest(self, offset, callback):
        print('Body read: ',self.body["response"] )
        callback( Characteristic.RESULT_SUCCESS, self.body["response"][offset:].encode('utf8') )
        #callback(  self.body["response"].encode('utf8') )
       

http_uriService = UriChrc()





class HttpControlPointChrc(Characteristic):
    
    # control application to request the API by methods
    
    CHRC_UUID = '00002aba-0000-1000-8000-00805f9b34fb'
    response=dict()
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2ABA',
            'properties': ['write'],
            'value': None }
            )

    
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        types = int(str(data.decode()))
        global to_Address , transactions , http_entity_body_chrc

        if types < 1 or types > 11:
            raise FailedException("0x80")
        elif types == 11:
            # cancel
            print('you canncel request')
        else:
            if types == 1:
                print('GET')
                status_code = self.GET_request()
                to_Address = ''
                transactions=''
            elif types == 3:
                print('POST')
                status_code = self.POST_request(to_Address,transactions)
                to_Address = ''
                transactions=''
            else:
                print('wrong type')
            HttpEntityBodyChrc.set_http_entity_body(HttpEntityBodyChrc,self.response)
            HttpStatusCodeChrc.set_http_status_code(HttpStatusCodeChrc,status_code)
        callback(Characteristic.RESULT_SUCCESS)

    def GET_request(self):
        import requests
        global http_uriService
        uri = http_uriService.getUri()
        r = requests.get(uri)
        self.response = r.json()
        return r.status_code 
    def POST_request(self,to_Address,transactions):
        import requests
        global http_uriService
        uri = http_uriService.getUri()
        payload = to_Address+','+transactions 
        datas = {'data':payload}
        r = requests.post( uri, data=datas)
        self.response = r.json()
        return r.status_code 

class HttpStatusCodeChrc(Characteristic):

    CHRC_UUID = '00002ab8-0000-1000-8000-00805f9b34fb'
    STATUS_BIT_BODY_RECEIVED = 4
    http_status_code = 0
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2AB8',
            'properties': ['read'],
            'value': None }
            )
        
        

    def set_http_status_code(self, value):
        self.http_status_code = value

    def onReadRequest(self, offset, callback):
        print('Status read: ',self.http_status_code )
        callback(Characteristic.RESULT_SUCCESS, str(self.http_status_code).encode('utf8'))


class HttpSecurityChrc(Characteristic):
    CHRC_UUID = '00002abb-0000-1000-8000-00805f9b34fb'
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2ABB',
            'properties': ['read'],
            'value': None }
            )
        self.set_value(False)
    def set_value(self, value):
        """Can be called from ctor or by client service to change default
        value."""
        self.https_security = value
    def onReadRequest(self, offset, callback):
        print('Security read: ',self.https_security )
        callback(Characteristic.RESULT_SUCCESS, str(self.https_security).encode('utf8'))







