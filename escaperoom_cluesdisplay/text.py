#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy, QGraphicsDropShadowEffect, \
    QFrame
from PyQt5.QtGui import QFont
from color import palette
import logging


class Text(QLabel):

    def __init__(self, text='', font_size=24, color='green',
                 font='Inconsolata', bloom_radius=16, debug=False,
                 *args, **kwargs):

        super().__init__(text, *args, **kwargs)
        self._init_style(font, font_size)
        self._init_bloom_effect(bloom_radius)
        self.set_color(color)

        if debug:
            self.setFrameStyle(QFrame.Box | QFrame.Raised)

    def setText(self, txt):
        try:
            super().setText(txt)
        except BaseException:
            logging.exception("Failed to set text")

    def set_color(self, color):
        """Set the text color"""
        c = palette[color]
        style_c = f'rgba({c.red()}, {c.green()}, {c.blue()}, {c.alpha()})'
        self.setStyleSheet('QLabel { color: ' + style_c + '; }')
        self.bloom.setColor(c)

    def set_alignement(self, a):
        try:
            alignments = {'left': Qt.AlignVCenter | Qt.AlignLeft,
                          'center': Qt.AlignCenter,
                          'right': Qt.AlignVCenter | Qt.AlignRight}
            self.setAlignment(alignments[a])
        except BaseException:
            logging.exception("Failed to set text alignment")

    def _init_style(self, font, font_size):
        """Create font, set size, alignement and word wrap"""
        self.setFont(QFont(font, font_size))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setMargin(64)

    def _init_bloom_effect(self, radius=32):
        """Create a bloom effect"""
        self.bloom = QGraphicsDropShadowEffect()
        self.bloom.setBlurRadius(radius)
        self.bloom.setXOffset(0)
        self.bloom.setYOffset(0)
        self.setGraphicsEffect(self.bloom)
