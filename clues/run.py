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

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import asyncio
from aiohttp import web
import json

class ServerSignals(QObject):
    received_clue = pyqtSignal(str)
    clear_clues = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threadpool = QThreadPool()
        self.create_layout()
        self.showFullScreen()
        self.start_server()

    def create_layout(self):
        self.clue = QLabel('hello')
        self.clue.setFont(QFont('Times', 36, QFont.Bold))
        self.clue.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clue.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.clue)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_server(self):
        server = Server()
        server.signals.received_clue.connect(self.set_clue)
        self.threadpool.start(server)
    
    def set_clue(self, text):
        self.clue.setText(text)

    def clear(self):
        self.clue.setText('')
    

class Server(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = ServerSignals()
        app = web.Application()
        app.add_routes([web.post('/', self.handle_post)])
        self.runner = web.AppRunner(app)

    @pyqtSlot()
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.runner.setup())
        site = web.TCPSite(self.runner, 'localhost', 8081)
        loop.run_until_complete(site.start())
        loop.run_forever()

    async def handle_post(self, request):
        params = await request.json() 
        self.signals.received_clue.emit(params['text'])
        return web.Response(content_type='application/json', text='done')

app = QApplication([])
window = MainWindow()
app.exec_()

