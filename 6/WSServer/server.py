#!c:\Python34\python.exe
# -*- coding: utf-8 -*-

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import json
import commands
import logging
import asyncio
from _thread import start_new_thread


class Temp:
    handlers = []


class Handler(WebSocketServerProtocol):
    def __init__(self):
        WebSocketServerProtocol.__init__(self)
        self.temp = Temp
        self.addr = None
        self.logger = logging.getLogger('WSServer')
        if not len(self.temp.handlers):
            self.id = 1
        else:
            self.id = max([handler.id for handler in self.temp.handlers]) + 1

    def ws_send(self, message):
        self.sendMessage(message.encode('utf-8'), False)

    def onConnect(self, request):
        self.temp.handlers.append(self)
        self.addr = request.peer[4:]
        self.logger.info('%s Запрос на подключение' % self.addr)
        commands.join(self, None)

    def onOpen(self):
        self.ws_send(json.dumps({
            'type': 'welcome',
            'data': {
                'message': 'arrows websocket server WELCOME!',
                'version': '1.0'
            }
        }))

    def onMessage(self, payload, is_binary):
        try:
            message = json.loads(payload.decode('utf-8'))
            message_type = message['type']
            data = message['data']
        except:
            message_type = 'error'
            data = 'Error'
        try:
            message_type = message_type.replace('__', '')
            self.logger.info('%s Запрос %s  %s' % (self.addr, message_type, data))
            resp = commands.__getattribute__(message_type)(self, data)
        except Exception as ex:
            resp = {'type': message_type + '_error', 'data': str(ex)}
            self.logger.error('%s Ошибка %s  %s' % (self.addr, message_type, str(ex)))
        self.ws_send(json.dumps(resp))
        self.logger.info('%s Ответ  %s  %s' % (self.addr, resp['type'], resp['data']))

    def onClose(self, *args):
        self.temp.handlers.remove(self)
        self.logger.info('%s Отключился' % (self.addr,))


def run(ip='0.0.0.0', port=8000):
    form = '[%(asctime)s]  %(levelname)s: %(message)s'
    logger = logging.getLogger("WSServer")
    logging.basicConfig(level=logging.INFO, format=form)

    log_handler = logging.FileHandler('logs/log.txt')
    log_handler.setFormatter(logging.Formatter(form))

    logger.addHandler(log_handler)
    logger.info('Запуск сервера %s:%s' % (ip, port))

    l = asyncio.get_event_loop()

    factory = WebSocketServerFactory(u"ws://%s:%s" % (ip, port))
    factory.protocol = Handler

    coro = l.create_server(factory, ip, port)
    s = l.run_until_complete(coro)

    start_new_thread(l.run_forever, tuple())
    return s, l


if __name__ == '__main__':
    server, loop = run()
    while True:
        try:
            inp = input()
            if inp[0] != '/':
                out = eval(inp)
                if out is not None:
                    print(out)
            else:
                if inp == '/stop':
                    log = logging.getLogger('WSServer')
                    log.info('Выключение сервера \n ---------------- \n\n')
                    exit()
        except Exception as ex:
            print(str(ex))
