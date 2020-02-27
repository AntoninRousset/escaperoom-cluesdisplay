#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from timer import Timer
from image import Gallery
from text import Text
import logging
from utils import iter_layout


class Background(QWidget):

    def __init__(self, images, background_size='fit', fullscreen=True,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.background = None
        self.background_size = background_size
        self.load_images(images)
        if fullscreen:
            self.showFullScreen()
        else:
            self.show()

    def load_images(self, images):
        self.images = {k: QPixmap(str(v)) for k, v in images.items()}

    def set_background(self, k):
        try:
            self.background = k
            self._resize_background()

        except BaseException:
            logging.exception('Failed to set background')

    def _resize_background(self):

        try:
            if not self.background:
                return

            img = self.images[self.background]

            if self.background_size == 'fit':
                self._bg = img.scaled(self.width(), self.height(),
                                      Qt.KeepAspectRatioByExpanding)
            else:
                self._bg = img.scaled(self.width(), self.height())

            self.update()

        except BaseException:
            logging.exception('Failed to resize background')

    def resizeEvent(self, event):
        self._resize_background()
        super().resizeEvent(event)

    def paintEvent(self, event):

        if not self.background:
            return

        painter = QPainter(self)
        x = int((self.width() - self._bg.width()) / 2)
        y = int((self.height() - self._bg.height()) / 2)
        painter.drawPixmap(x, y, self._bg)
        super().paintEvent(event)


class MainWindow(QMainWindow, Background):

    def __init__(self, images, layout_mode='timer image clue', debug=False,
                 *args, **kwargs):

        super().__init__(images, *args, **kwargs)

        images = {
            'vessel_gg': 'vessel_gg.png',
            'vessel_rg': 'vessel_rg.png',
            'vessel_gr': 'vessel_gr.png',
            'vessel_rr': 'vessel_rr.png',
            'vessel_rx': 'vessel_rx.png',
            'vessel_xr': 'vessel_xr.png',
            'vessel_gx': 'vessel_gx.png',
            'vessel_xg': 'vessel_xg.png',
        }

        self.timer = Timer(debug=debug)
        self.image = Gallery(images, debug=debug)
        self.clue = Text(debug=debug)

        self._init_layout()
        self.set_layout(layout_mode)

    def connect_signals(self, signals):
        signals.cmd_layout.connect(self.set_layout)
        signals.cmd_alignment.connect(self.clue.set_alignement)
        signals.cmd_color.connect(self.set_color)
        signals.cmd_clue.connect(self.clue.setText)
        signals.cmd_timer_speed.connect(self.timer.set_speed)
        signals.cmd_timer_time.connect(self.timer.set_time)
        signals.cmd_image.connect(self.image.set)
        signals.cmd_background.connect(self.set_background)
        signals.cmd_power.connect(self.set_power)

    def _init_layout(self):
        self.v_layout = QVBoxLayout()
        self.v_widget = QWidget()
        self.v_widget.setLayout(self.v_layout)

        self.h_layout = QHBoxLayout()
        self.h_layout.setContentsMargins(100, 0, 100, 0)
        self.h_layout.setSpacing(20)
        self.h_widget = QWidget()
        self.h_widget.setLayout(self.h_layout)

        central_widget = QWidget()
        central_widget.setLayout(self.v_layout)
        self.setCentralWidget(central_widget)

    def set_layout(self, layout_mode):

        try:

            widgets = {'timer': self.timer,
                       'clue': self.clue,
                       'image': self.image}
            widgets = [widgets[w] for w in layout_mode.split()]

            if not widgets:
                return

            self._empty_layouts()

            self.v_layout.addWidget(widgets[0])

            if len(widgets) > 1:
                self.v_layout.addWidget(self.h_widget)
                for w in widgets[1:]:
                    self.h_layout.addWidget(w)

        except BaseException:
            logging.exception('Failed to set layout')

    def _empty_layouts(self):

        widgets = list(iter_layout(self.v_layout))
        for w in widgets:
            self.v_layout.removeWidget(w)
            w.setParent(None)

        widgets = list(iter_layout(self.h_layout))
        for w in widgets:
            self.h_layout.removeWidget(w)
            w.setParent(None)

    def set_color(self, color):
        try:
            self.timer.set_color(color)
            self.clue.set_color(color)
        except BaseException:
            logging.exception('Failed to set color')

    def set_power(self, state):
        try:
            self.centralWidget().setVisible(state)
        except BaseException:
            logging.exception("Failed to set power")
