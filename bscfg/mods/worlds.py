# -*- coding: utf-8 -*-
import bs
import settings
import bsGame


def night():
    try:
        # print 'Nigth Mode: ', settings.nightMode
        if settings.nightMode:
            bs.getSharedObject("globals").tint = (0.6, 0.8, 1.2)
    except:
        pass


def main():
    night()
