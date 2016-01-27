import logging
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
import urllib2,urllib
from flask.json import dumps
import traceback
import time

from yowsup.layers.network import YowNetworkLayer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()

# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.handlers=[ch]


class RobotLayer(YowInterfaceLayer):

    def __init__(self):
        super(RobotLayer, self).__init__()


    @ProtocolEntityCallback("success")
    def onSuccess(self, successProtocolEntity):
        app=self.getProp('flaskApp')
        if not hasattr(app,'layers'):
            app.layers={}
        credentials=":".join(self.getProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS))
        app.layers[credentials]=self
        logger.info('Success! Connected to '+ self.getProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS)[0])


    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        url=self.getProp('url')
        try:
            #assert(isinstance(messageProtocolEntity, TextMessageProtocolEntity))
            sender=messageProtocolEntity.getFrom().split('@')[0]
            name=messageProtocolEntity.getNotify().decode('utf-8')
            body=messageProtocolEntity.getBody().decode('utf-8')
            values = {u'message': {u'date': 1444296978
                                ,u'contact': {u'phone_number': unicode(sender)
                                            , u'first_name': name
                                            , u'last_name': u''
                                            , u'user_id': sender}
                                , u'text': body
                                , u'from': {u'first_name': name, u'last_name': u'', u'id': sender}
                                , u'chat': {u'first_name': name, u'last_name': u'', u'id': sender}
                                ,u'message_id':1234323456
                                }
                      ,u'update_id':12323456
                    }
            logger.info('sending %(values)s to url %(url)s'%dict(values=str(values),url=url))
            #data = urllib.urlencode(values)
            req = urllib2.Request(url, dumps(values))
            req.add_header('Content-Type','application/json')
            rsp = urllib2.urlopen(req)
            content = rsp.read()
            print content
        except Exception as e:
            logger.exception('Exception when receiving message')
            traceback.print_exc(e)

        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())


    # def onTextMessage(self,messageProtocolEntity):
    #     print str(messageProtocolEntity)
    #     # just print info
    #     print("Echoing %s to %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))

    # def onMediaMessage(self, messageProtocolEntity):
    #     # just print info
    #     if messageProtocolEntity.getMediaType() == "image":
    #         print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))
    #
    #     elif messageProtocolEntity.getMediaType() == "location":
    #         print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))
    #
    #     elif messageProtocolEntity.getMediaType() == "vcard":
    #         print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))

    def onEvent(self, layerEvent):
        credentials=self.getProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS)
        id=str(credentials[0])
        logger.info(id +': '+ layerEvent.getName())
        if layerEvent.getName() == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            logger.warning("Id: %s, Disconnected: %s" % (id,layerEvent.getArg("reason")))
            if layerEvent.getArg("reason") in ('Connection Closed','Ping Timeout'):
                time.sleep(20)
                logger.info("Id: %s, Issueing EVENT_STATE_CONNECT" % id)
                self.getStack().broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
            else:
                app=self.getProp('flaskApp')
                if hasattr(app,'layers') and 'credentials'  in app.layers:
                    del app.layers[credentials]
        elif layerEvent.getName() == YowNetworkLayer.EVENT_STATE_CONNECTED:
            logger.info("Id: %s Connected"% id)