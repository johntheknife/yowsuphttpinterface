from yowsup.stacks import YowStack
from .layer import RobotLayer
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth                        import YowCryptLayer, YowAuthenticationProtocolLayer, AuthError
from yowsup.layers.coder                       import YowCoderLayer
from yowsup.layers.network                     import YowNetworkLayer
from yowsup.layers.protocol_messages           import YowMessagesProtocolLayer
from yowsup.layers.protocol_media              import YowMediaProtocolLayer
from yowsup.layers.stanzaregulator             import YowStanzaRegulator
from yowsup.layers.protocol_receipts           import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks               import YowAckProtocolLayer
from yowsup.layers.logger                      import YowLoggerLayer
from yowsup.layers.protocol_iq                 import YowIqProtocolLayer
from yowsup.layers.protocol_calls              import YowCallsProtocolLayer
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.common import YowConstants
from yowsup import env
import sys, threading
import urllib,urllib2
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YowsupRobotStack(object):
    def __init__(self, credentials, encryptionEnabled = False,interactionProtocol=None,url=None,flaskApp=None):
        if encryptionEnabled:
            from yowsup.layers.axolotl                     import YowAxolotlLayer
            layers = (
                RobotLayer,
                (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer, YowMediaProtocolLayer, YowIqProtocolLayer, YowCallsProtocolLayer),
                YowAxolotlLayer,
                YowLoggerLayer,
                YowCoderLayer,
                YowCryptLayer,
                YowStanzaRegulator,
                YowNetworkLayer
            )
        else:
            layers = (
                RobotLayer,
                (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer, YowMediaProtocolLayer, YowIqProtocolLayer, YowCallsProtocolLayer),
                YowLoggerLayer,
                YowCoderLayer,
                YowCryptLayer,
                YowStanzaRegulator,
                YowNetworkLayer
            )

        self.stack = YowStack(layers)
        self.stack.setCredentials(credentials)
        self.stack.setProp('url',url)
        self.stack.setProp('flaskApp',flaskApp)

    def start(self):
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        def startThread():
            try:
                self.stack.loop(timeout = 0.5, discrete = 0.5)
            except AuthError as e:
                print("Auth Error, reason %s" % e)
            except KeyboardInterrupt:
                print("\nYowsdown KeyboardInterrupt")
                sys.exit(0)
            except Exception as e:
                print("\nYowsdown General Exception")
                print e
        t1=threading.Thread(target=startThread)
        t1.daemon=True
        t1.start()



