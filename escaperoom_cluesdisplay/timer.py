#!/usr/bin/env python
# -*- coding: utf-8 -*-

from text import Text
from PyQt5.QtCore import Qt, QElapsedTimer, QTimer
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QSizePolicy, QFrame
import logging


class Timer(Text):

    def __init__(self, font_size=100, debug=False):

        super().__init__(font_size=font_size)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)

        self.speed = False
        self.seconds = 0.0
        self._elapsed_time = QElapsedTimer()
        self._timer = QTimer(self, interval=100, timeout=self._update)
        self._timer.timeout.connect(self._update)
        self._timer.start()

        if debug:
            self.setFrameStyle(QFrame.Box | QFrame.Raised)

    def set_current_state(self, state):

        self._current_state = state
        self.stateChanged.emit(state)

    def set_speed(self, speed):
        try:
            self.speed = float(speed)
            self._elapsed_time.start()
        except BaseException:
            logging.exception("Failed to set timer speed")

    def set_time(self, time):

        try:
            time = time.strip()

            if time[0] in '+-':
                self.seconds += float(time)
            else:
                self.seconds = float(time)
        except BaseException:
            logging.exception("Failed to set timer time")

    @pyqtSlot()
    def _update(self):
        self.seconds += self.speed * self._elapsed_time.elapsed() / 1000
        self.seconds = max(self.seconds, 0)
        self._elapsed_time.start()
        h, m, s = self.split_time(self.seconds)
        self.setText(f'{h:02}:{m:02}:{s:02}')

    @classmethod
    def split_time(cls, seconds):

        hours, remaining = divmod(seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        return int(hours), int(minutes), int(seconds)
