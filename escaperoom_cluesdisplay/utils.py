#!/usr/bin/env python
# -*- coding: utf-8 -*-


def iter_layout(layout):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item:
            yield item.widget()


def clear_layout(layout):
    for i in range(layout.count()):
        layout.removeAt(i)
