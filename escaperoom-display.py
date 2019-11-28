#!/usr/bin/env python

'''
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, version 3.
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import asyncio, json, argparse
from aiohttp import web
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_layout()
        self.showFullScreen()

    def create_layout(self):
        self.clue = QLabel('')
        self.clue.setFont(QFont('Times', 36, QFont.Bold))
        self.clue.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clue.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.clue)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def connect_server(self, server):
        server.signals.received_clue.connect(self.set_clue)
        server.signals.clear_clues.connect(self.clear)
    
    def set_clue(self, text):
        self.clue.setText(text)

    def clear(self):
        self.clue.setText('')
    
class ServerSignals(QObject):
    received_clue = pyqtSignal(str)
    clear_clues = pyqtSignal()

class Server(QRunnable):
    def __init__(self, host, port):
        super().__init__()
        self.host = host;
        self.port = port;
        self.signals = ServerSignals()
        self.app = web.Application()
        self.app.add_routes([web.post('/', self.handle_post)])

    @pyqtSlot()
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = web.AppRunner(self.app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, self.host, self.port)
        print(f'Server on {self.host}:{self.port}')
        loop.run_until_complete(site.start())
        loop.run_forever()

    async def handle_post(self, request):
        params = await request.json() 
        self.signals.received_clue.emit(params['text'])
        return web.Response(content_type='application/json', text='done')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EscapeRoom server')
    parser.add_argument('--host', type=str, default='0.0.0.0',
        help='Host for the HTTP server (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080,
            help='Port for HTTP server (default: 8080)')
    args = parser.parse_args()

    app = QApplication([])
    window = MainWindow()
    server = Server(host=args.host, port=args.port)
    window.connect_server(server)
    pool=QThreadPool()
    pool.start(server)
    app.exec_()
