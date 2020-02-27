#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QFrame
import logging


class Gallery(QLabel):

    def __init__(self, images, debug=False, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if debug:
            self.setFrameStyle(QFrame.Box | QFrame.Raised)

        self.setAlignment(Qt.AlignCenter)
        self.load_images(images)
        self.set(None)

    def load_images(self, images):

        self.images = {k: QPixmap(str(v)) for k, v in images.items()}

    def set(self, k):

        try:

            try:
                img = self.images[k]
                self.setPixmap(img)
                self.setVisible(True)
            except (TypeError, KeyError):
                img = None
                self.setVisible(False)

        except BaseException:
            logging.exception("Failed to set image in gallery")
