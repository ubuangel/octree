#!/usr/bin/env python
#-*- coding: utf8 -*-


class Color(object):
    """
    Color class
    """

    def __init__(self, red=0, green=0, blue=0, alpha=None):
        """
        inicializar color
        """
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
