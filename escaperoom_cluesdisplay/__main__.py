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

import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication
import logging
import argparse

from . import ROOT
from .window import MainWindow


class CluesDisplaySignals(QObject):
    cmd_layout = pyqtSignal(str)
    cmd_alignment = pyqtSignal(str)
    cmd_color = pyqtSignal(str)
    cmd_clue = pyqtSignal(str)
    cmd_timer_speed = pyqtSignal(float)
    cmd_timer_time = pyqtSignal(str)
    cmd_image = pyqtSignal(str)
    cmd_background = pyqtSignal(str)
    cmd_power = pyqtSignal(bool)


class Piper(QRunnable):

    def __init__(self):

        super().__init__()
        self.signals = CluesDisplaySignals()

    @pyqtSlot()
    def run(self):

        for line in sys.stdin:

            try:

                # remove final '\n' and split cmd and [arguments]
                line = line.strip().split(maxsplit=1)
                if len(line) == 1:
                    cmd = line[0]
                    args = ''
                else:
                    cmd, args = line
                    args = args.replace(r'\n', '\n')

                if cmd == 'layout':
                    self.signals.cmd_layout.emit(args)

                elif cmd == 'alignment':
                    self.signals.cmd_alignment.emit(args)

                elif cmd == 'color':
                    self.signals.cmd_color.emit(args)

                elif cmd == 'clue':
                    self.signals.cmd_clue.emit(args)

                elif cmd == 'timer':
                    args = args.split()
                    if len(args) >= 1:
                        self.signals.cmd_timer_speed.emit(float(args[0]))
                    if len(args) >= 2:
                        self.signals.cmd_timer_time.emit(args[1])

                elif cmd == 'image':
                    self.signals.cmd_image.emit(args)

                elif cmd == 'background':
                    self.signals.cmd_background.emit(args)

                elif cmd == 'power':
                    self.signals.cmd_power.emit(not args == 'off')

                else:
                    raise ValueError(line)

            except BaseException:
                logging.exception('External cmd execution failure')

def read_args():

    parser = argparse.ArgumentParser(description='Clue display for escaperoom')
    parser.add_argument('--poweroff', default=True, action='store_true',
                        help='Start with the display turned off')
    parser.add_argument('--color', type=str, default='green',
                        help='Initial color of the display')
    parser.add_argument('--background', type=str, default='green',
                        help='Initial background')
    return parser.parse_args()


def main():
    args = read_args()

    # application
    app = QApplication([])

    app.setOverrideCursor(Qt.BlankCursor)

    # main window
    window = MainWindow({'green': ROOT / 'bg_green.png',
                         'red': ROOT / 'bg_red.png'},
                        fullscreen=True, debug=False,
                        size=app.desktop().screenGeometry().size())
    try:
        window.set_power(not args.poweroff)
        window.set_color(args.color)
        window.set_background(args.background)
    except BaseException:
        logging.exception('Failed to exec args')

    # signals
    piper = Piper()
    window.connect_signals(piper.signals)
    pool = QThreadPool()
    pool.start(piper)
    app.exec()

if __name__ == '__main__':
    main()
