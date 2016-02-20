#!/usr/bin/env python


import os,logging
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from robot import yowsup
from flask import Flask,g,request,Response
from flask.json import dumps
app=Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def sendAsFlaskJson(message,ok):
    result= Response(dumps(dict(ok=ok,description=message)))
    result.headers['Content-Type']='application/json'
    return result

@app.route("/<credentials>/sendMessage", methods=[ 'POST'])
def sendMessageToWA(credentials):
    credentials=str(credentials).replace('~slash~','/').replace('~plus~','+')
    if not hasattr(app,'layers') or credentials not in app.layers:
        return sendAsFlaskJson(ok=False,message='YowsupLayer not available')
    jsonInput=request.get_json()

    if 'text' in jsonInput and 'chat_id' in jsonInput:
        content=jsonInput['text'].encode('utf-8')
        phone=str(jsonInput['chat_id'])
        if '@' in phone:
            messageEntity = TextMessageProtocolEntity(content, to = phone)
        elif '-' in phone:
            messageEntity = TextMessageProtocolEntity(content, to = "%s@g.us" % phone)
        else:
            messageEntity = TextMessageProtocolEntity(content, to = "%s@s.whatsapp.net" % phone)
        #self.yowsupLayer.ackQueue.append(messageEntity.getId())
        app.layers[credentials].toLower(messageEntity)
        result=Response(dumps({"ok":True
              ,"result":{"message_id":311
                        ,"from":{"id":phone
                                ,"first_name":""
                                ,"username":""}
                        ,"chat":{"id":phone
                                ,"first_name":""
                                ,"last_name":""
                                ,"type":"private"}
                        ,"date":1450275059
                        ,"text":jsonInput['text']
                        }
                }))
        result.headers['Content-Type']='application/json'
    return result

@app.route("/<credentials>/disconnect",methods=['GET','POST'])
def stopStack(credentials):
    credentials=str(credentials).replace('~slash~','/').replace('~plus~','+')
    if hasattr(app,'layers') and credentials in app.layers:
        app.layers[credentials].disconnect()
        return 'Disconnecting layer for id '+credentials.split(':')[0]
    else:
        return 'There is no layer for id '+credentials.split(':')[0]


@app.route("/<credentials>/setWebhook", methods=['GET', 'POST'])
def startStackWithCredentials(credentials):
    input_json=request.get_json()
    logging.info(input_json)
    url=input_json['url']
    credentials=str(credentials).replace('~slash~','/').replace('~plus~','+')
    if hasattr(app,'layers') and credentials in app.layers:
        app.layers[credentials].connect()
        resp=Response('{"ok":true,"result":true,"description":"Connecting layer for id '+credentials.split(':')[0]+'"}')
    else:
        stack = yowsup.YowsupRobotStack(tuple(credentials.split(":")),encryptionEnabled=True,url=url,flaskApp=app)
        stack.start()
        resp=Response( '{"ok":true,"result":true,"description":"Attempting stack for id %s pointing at %s"}'%( credentials.split(':')[0],url))
    resp.headers['Content-Type']="application/json"
    return resp


if __name__ == "__main__":
    try:
        myport=os.environ.get('runInPort')
        if myport is None:
            myport="5000"
        myport=int(myport)
        app.run(host='0.0.0.0',port=myport)
    except Exception as e:
        import traceback
        print traceback.print_exc()
        if hasattr(app,'layers'):
            for layer in app.layers:
                layer.disconnect()




