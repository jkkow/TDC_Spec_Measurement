from sources.TDC_SpecMeasure import *
from sources.FindSerial import *
import time
import numpy as np

import unittest


class getdata(object):
    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        self.y1 = np.sin(2 * np.pi * 0.1 * self.i)
        self.y2 = np.cos(2 * np.pi * 0.1 * self.i)
        return self.i, self.y1, self.y2


class Test_TDC_SpecMeasure(unittest.TestCase):
    def test_data(self):
        data = getdata()
        fig, ax = plt.subplots()
        tdc = TDC_SpecMeasure(ax, data)
        fig.canvas.mpl_connect("key_press_event", tdc)
        plt.show()
