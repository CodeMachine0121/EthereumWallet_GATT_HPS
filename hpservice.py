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
        to_Address += str(data.decode())
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
        print(transactions)
        transactions += str(data.decode())
        callback(Characteristic.RESULT_SUCCESS)
    
    def onReadRequest(self,offset,callback):
        global transactions
        callback(Characteristic.RESULT_SUCCESS, transactions.encode('utf8'))


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
        global uri
        uri = 'http://localhost:5000/'+value
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
    body=''
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2AB9',
            'properties': ['read'],
            'value': None }
            )
        self.body = str()
    
    def set_http_entity_body(self,value):
        print('body value you set: ',value)
        self.body = value
    
    def get_http_entity_body(self):
        return self.body

    
    def onReadRequest(self, offset, callback):
        print('Body read: ',self.body)
        callback(Characteristic.RESULT_SUCCESS, self.body[offset:])



http_uriService = UriChrc()
http_entity_body_chrc = HttpEntityBodyChrc()




class HttpControlPointChrc(Characteristic):
    
    # control application to request the API by methods
    
    CHRC_UUID = '00002aba-0000-1000-8000-00805f9b34fb'
    response=''
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2ABA',
            'properties': ['read','write'],
            'value': None }
            )
    def onReadRequest(self,offset,callback):
        print('Response: ',self.response)
        callback(Characteristic.RESULT_SUCCESS, self.response.encode('utf8'))


    def onWriteRequest(self, data, offset, withoutResponse, callback):
        types = int(str(data.decode()))
        global to_Address , transactions

        if types < 1 or types > 11:
            raise FailedException("0x80")
        elif types == 11:
            # cancel
            print('you canncel request')
        else:
            if types == 1:
                print('GET')
                self.GET_request()
                to_Address = ''
                transactions=''
            elif types == 3:
                print('POST')
                self.POST_request(to_Address,transactions)
                to_Address = ''
                transactions=''
            else:
                print('wrong type')
        callback(Characteristic.RESULT_SUCCESS)

    def GET_request(self):
        import requests
        global http_uriService
        uri = http_uriService.getUri()
        r = requests.get(uri)
        self.response = r.text

       

    def POST_request(self,to_Address,transactions):
        import requests
        global http_uriService
        uri = http_uriService.getUri()

        payload = to_Address+','+transactions
        datas = {'data':payload}
        r = requests.post( uri, data=datas)
        self.response = r.text
        

class HttpStatusCodeChrc(Characteristic):

    CHRC_UUID = '00002ab8-0000-1000-8000-00805f9b34fb'
    STATUS_BIT_BODY_RECEIVED = 4
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2AB8',
            'properties': ['read'],
            'value': None }
            )
        self.http_status_code = 0
        self.set_http_status_code(self.http_status_code)
        

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



