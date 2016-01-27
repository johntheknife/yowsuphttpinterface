# yowsuphttpinterface

You can use this project to emulate telegram's bot api with a whatsapp account. You have a Dockerfile and a Docker-compose setup so you can easily set it up in your own cloud.

The first thing you need is to get the credentials for your whatsapp account, and for that you should go through the registration flow in yowsup's project. After you have run this flow, you should have your credentials as a colon-separated string which I call your credentials:

    447372753450:FTw0OetHWbvY0ubMHBJkZntGzRM=

Beware that some credentials use special characters like / and + that are not well parsed by flask. For those cases, you should replace '/' with '~slash~' and '~plus~' with '+' as I do the opposite replacement in the code.

    credentials=str(credentials).replace('~slash~','/').replace('~plus~','+')

Once your credentials have been established, you can use all the web services described under yowsupflask.py:
- /\<credentials\>/sendMessage - Used to send messages to another whatsapp account
- /\<credentials\>/setWebhook - Used to start listening to messages to the whatsapp account, a url should be provided
- /\<credentials\>/disconnect - Used to disconnect from the whatsapp account

Note that you should be able to connect to this API from python using the regular telegram API for bots in python. All you need to do is:

    bot= Bot(token=<credentials>,base_url=<url_of_your_webservice>)

# TODO:

1.- So far, I have only been able to connect to one account simultaneously from one container (Any help on this regard would be very appreciated). That is why I have multiple containers in the docker-compose setup. You can do the same thing: prepare as many services as accounts you need to listen to. Beware of the **runInPort** parameter in docker-compose.yml as it defines the port that your http web service will be listening to and it should be the same as your ports parameter.

2.- Every one in a while the thread disconnects. I do capture the disconnect event and connect again after 20 seconds. This is far from nice, but, again, what can I do?

3.- Logging is not nice either, I get two entries for each log.

4.- Finally, after a couple weeks running, I have seen this thread, which has forced a disconnect:

    Traceback (most recent call last):
      File "/usr/lib/python2.7/threading.py", line 801, in __bootstrap_inner
        self.run()
      File "/usr/lib/python2.7/threading.py", line 754, in run
        self.__target(*self.__args, **self.__kwargs)
      File "/src/yowsup/stacks/yowstack.py", line 204, in discreteLoop
        asyncore.loop(*args, **kwargs)
      File "/usr/lib/python2.7/asyncore.py", line 216, in loop
        poll_fun(timeout, map)
      File "/usr/lib/python2.7/asyncore.py", line 156, in poll
        read(obj)
      File "/usr/lib/python2.7/asyncore.py", line 87, in read
        obj.handle_error()
      File "/usr/lib/python2.7/asyncore.py", line 83, in read
        obj.handle_read_event()
      File "/usr/lib/python2.7/asyncore.py", line 449, in handle_read_event
        self.handle_read()
      File "/src/yowsup/layers/network/layer.py", line 86, in handle_read
        self.receive(data)
      File "/src/yowsup/layers/network/layer.py", line 94, in receive
        self.toUpper(data)
      File "/src/yowsup/layers/__init__.py", line 59, in toUpper
        self.__upper.receive(data)
      File "/src/yowsup/layers/stanzaregulator/layer.py", line 28, in receive
        self.processReceived()
      File "/src/yowsup/layers/stanzaregulator/layer.py", line 48, in processReceived
        self.toUpper(oneMessageData)
      File "/src/yowsup/layers/__init__.py", line 59, in toUpper
        self.__upper.receive(data)
      File "/src/yowsup/layers/auth/layer_crypt.py", line 63, in receive
        self.toUpper(payload)
      File "/src/yowsup/layers/__init__.py", line 59, in toUpper
        self.__upper.receive(data)
      File "/src/yowsup/layers/coder/layer.py", line 35, in receive
        self.toUpper(node)
      File "/src/yowsup/layers/__init__.py", line 59, in toUpper
        self.__upper.receive(data)
      File "/src/yowsup/layers/logger/layer.py", line 14, in receive
        self.toUpper(data)
      File "/src/yowsup/layers/__init__.py", line 59, in toUpper
        self.__upper.receive(data)
      File "/src/yowsup/layers/axolotl/layer.py", line 126, in receive
        self.toUpper(protocolTreeNode)
      File "/src/yowsup/layers/__init__.py", line 59, in toUpper
        self.__upper.receive(data)
      File "/src/yowsup/layers/__init__.py", line 169, in receive
        s.receive(data)
      File "/src/yowsup/layers/__init__.py", line 105, in receive
        recv(node)
      File "/src/yowsup/layers/auth/layer_authentication.py", line 89, in handleStreamError
        raise AuthError("Unhandled stream:error node:\n%s" % node)
    AuthError: Unhandled stream:error node:
    <stream:error>
    <system-shutdown>
    </system-shutdown>
    </stream:error>