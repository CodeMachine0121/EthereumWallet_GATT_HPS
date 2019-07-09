from pybleno import *
import array
import struct
import sys
import traceback
from builtins import str
from hpservice import *
class HPS_Service(BlenoPrimaryService):
    def __init__(self):
        BlenoPrimaryService.__init__(self,{
            'uuid': '1823',
            'characteristics':[
                UriChrc(),
                HttpHeadersChrc(),
                HttpEntityBodyChrc(),
                HttpControlPointChrc(),
                HttpStatusCodeChrc(),
                HttpSecurityChrc(),
                SetToAddress(),
                SetTransaction()
            ]
        })

