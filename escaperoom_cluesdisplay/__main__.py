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

import asyncio, json, re, sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pathlib import Path
from atomicwrites import atomic_write
from collections import defaultdict

from . import ROOT

colors = {
        'green' : QColor(0, 255, 0, 180),
        'red' : QColor(255, 0, 0, 180)
        }

class Label(QLabel):

    def __init__(self, font_size=36, color=colors['green']):

        super().__init__('')

        self.setFont(QFont('Inconsolata', font_size))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(52)
        self.set_color(color)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.setGraphicsEffect(self.shadow)


        shadow = QGraphicsDropShadowEffect()

    def set_color(self, c):
        style_c = f'rgba({c.red()}, {c.green()}, {c.blue()}, {c.alpha()})'
        self.setStyleSheet('QLabel { color: '+style_c+'; }')
        self.shadow.setColor(c)


class Chronometer(Label):

    @classmethod
    def cut_seconds(cls, seconds):
        hours, remaining = divmod(seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        return int(hours), int(minutes), int(seconds)

    def __init__(self):

        super().__init__()

        self.running = False
        self.seconds = 0.0
        self._elapsed_time = QElapsedTimer()
        self._timer = QTimer(self, interval=100, timeout=self._update)
        self._timer.timeout.connect(self._update)
        self._timer.start()

    def setCurrentState(self, state):
        self._current_state = state
        self.stateChanged.emit(state)

    def set(self, running, seconds):
        self._elapsed_time.start()
        self.running = running
        self.seconds = seconds

    @pyqtSlot()
    def _update(self):
        seconds = self.seconds
        if self.running:
            seconds += self._elapsed_time.elapsed()/1000
        h, m, s = self.cut_seconds(seconds)
        self.setText(f'{h:02}:{m:02}:{s:02}')


class ClueLabel(Label):

    def __init__(self):

        super().__init__()


class ClueHistory:

    def __init__(self, histpath, hist_len=1000):
        self.hist = []
        self.hist_len = hist_len
        self.histpath = Path(histpath)
        self.load_histfile(self.histpath)

    def load_histfile(self, path):
        if path.exists():
            with open(path) as f:
                self.hist = [l.strip() for l in f]
        else:
            path.touch()

    def add(self, msg):
        self.hist.append(msg)
        with atomic_write(self.histpath, overwrite=True) as f:
            f.write('\n'.join(self.hist[-self.hist_len:]) + '\n')

    def suggestions(self, n=10):
        sugg = [l for l, _ in sorted(self._get_occurences().items(),
                                     key=lambda v: v[1],
                                     reverse=True)]
        return sugg[:n]

    def _get_occurences(self):
        occ = defaultdict(int)
        for k in self.hist:
            occ[k] += 1
        return occ


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_layout()
        self.showFullScreen()

    def paintEvent(self, event):

        pixmap = QPixmap()
        pixmap.load(str(ROOT/'background.png'))

        win_size = [self.width(), self.height()]
        win_aspect = self.width() / self.height()

        img_size = [pixmap.width(), pixmap.height()]
        img_aspect = pixmap.width() / pixmap.height()

        # img flatter than window -> fit height
        if img_aspect > win_aspect:
            scaling_factor = win_size[1] / img_size[1]
        # img flatter than window -> fit width 
        else:
            scaling_factor = win_size[0] / img_size[0]

        # fit height
        img_size[0] *= scaling_factor
        img_size[1] *= scaling_factor

        pixmap = pixmap.scaled(*img_size)
        painter = QPainter(self)
        center = [(win_size[0] - img_size[0]) / 2,
                  (win_size[1] - img_size[1]) / 2]
        painter.drawPixmap(*center, pixmap)

    def set_color(self, color):
        self.chronometer.set_color(color)
        self.clue.set_color(color)

    def create_layout(self):
        self.chronometer = Chronometer()
        self.chronometer.setFont(QFont('Inconsolata', 80, QFont.Bold))
        self.chronometer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chronometer.setAlignment(Qt.AlignCenter)

        self.clue = ClueLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.chronometer)
        layout.addWidget(self.clue)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def connect_signals(self, signals):
        signals.received_clue.connect(self.set_clue)
        signals.clear_clues.connect(self.clear)
        signals.received_chronometer.connect(self.chronometer.set)
        signals.set_color.connect(self.set_color)

    def set_clue(self, text, secret=False):
        self.clue.setText(text)

    def clear(self):
        self.clue.setText('')


class CluesDisplaySignals(QObject):
    received_clue = pyqtSignal(str)
    clear_clues = pyqtSignal()
    received_chronometer = pyqtSignal(bool, float)
    set_color = pyqtSignal(QColor)


class Piper(QRunnable):

    def __init__(self, clue_hist_file='clues.hist', default_nb_of_suggestions=10):
        super().__init__()
        self.clue_history = ClueHistory(clue_hist_file)
        self.default_nb_of_suggestions = default_nb_of_suggestions
        self.signals = CluesDisplaySignals()

    @pyqtSlot()
    def run(self):
        for line in sys.stdin:
            words = line.split(maxsplit=1)
            try:
                if words[0] == 'clue':
                    try:
                        clue = words[1][:-1].replace('\\n', '\n')
                        self.signals.received_clue.emit(clue)
                    except IndexError:
                        self.signals.received_clue.emit('')
                elif words[0] == 'chronometer':
                    words = words[1].split()
                    running, seconds = bool(float(words[0])), float(words[1])
                    self.signals.received_chronometer.emit(running, seconds)
                elif words[0] == 'power':
                    if words[1] == 'on':
                        print('not implemented')
                    elif words[1] == 'off':
                        print('not implemented')
                elif words[0] == 'color':
                    self.signals.set_color.emit(colors[words[1][:-1]])

            except Exception as e:
                print('com error', e)

    async def handle_suggestions(self, request):
        if request.method == 'POST':
            params = await request.json()
            n = params.get('n', self.default_nb_of_suggestions)
        else:
            n = self.default_nb_of_suggestions
        suggestions = self.clue_history.suggestions(n)
        return web.Response(content_type='application/json',
                            text=json.dumps({'clues': suggestions}))


def main():
    app = QApplication([])
    window = MainWindow()
    window.setFixedSize(app.desktop().screenGeometry().size())
    app.setOverrideCursor(Qt.BlankCursor)
    piper = Piper()
    window.connect_signals(piper.signals)
    pool = QThreadPool()
    pool.start(piper)
    app.exec()

if __name__ == '__main__':
    main()
