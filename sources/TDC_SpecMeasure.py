"""
Two channel powermerter로 부터의 측정값을 저장하고 실시간 plot하기 위한 함수 라이브러리.

V1.0 에서 파일 저장경로 변경 및 측정데이터 삭제기능 추가

Author: jkkow
Created: 2017-11-08T02:46:52
Last updated:
"""
# from FindSerial import *
import matplotlib.pyplot as plt
import xlsxwriter as xlw    # library for handling Excel file.
import numpy as np


class XY_DataGen(object):
    # This class reads measured data from device and return the data set whenever it is called.
    # In this project, the data comes from Aruduino Uno board that connected
    # to Dual channel powermeter. The Aruduino emits two line of data at a
    # time, one line for chennel 1 and the other for channel 2.

    def __init__(self, device):
        # get `serial` instance from device that is connected via serial
        # communication. If you use customized `FindSerial` class, make sure the
        # device instace as like `aruino.serialport`.
        self.device = device
        self.x = 0  # set start value as zero for mesurement steps

    def __call__(self):
        self.x += 1  # increase measurement step
        self.device.write('r'.encode())
        self.y1 = int(self.device.readline().decode())  # read data y1 from the device
        self.y2 = int(self.device.readline().decode())

        return [self.x, self.y1, self.y2]


class TDC_SpecMeasure(object):
    def __init__(self, ax, data):
        # Core role of this __init_() function is intializing the graph configuration.
        self.ax = ax  # get 'ax' object
        self.xy_data = data  # get a function that returns measured data values as initial parameter

        self.ax.set_title("TDC Examination", fontsize=15)
        self.ax.set_xlabel("Dial Ticks", fontsize=13, labelpad=12)
        self.ax.set_ylabel("Power(A.U.)", fontsize=13, labelpad=12)
        self.ax.set_yticklabels([])

        self.xmin_init, self.xmax_init = 0, 10  # set initial xmin, xmax for plot range
        self.ymin_init, self.ymax_init = -0.2, 1.1  # set initial ymin, ymax for plot range
        # axes range setting
        self.ax.set_xlim(self.xmin_init, self.xmax_init)
        self.ax.set_ylim(self.ymin_init, self.ymax_init)

        self.x_list = []    # make empty list for x data
        self.y1_list, self.y2_list = [], []  # make emepty list for y1, y2 data

        self.line1, = self.ax.plot(self.x_list, self.y1_list, '-o',
                                   label="Ch_1")   # plot line1 for data y1
        self.line2, = self.ax.plot(self.x_list, self.y2_list, '-x',
                                   label="Ch_2")   # plot line2 for data y2
        self.ax.legend(loc=0, fontsize=12)

    def __call__(self, event):
        # This magic method is called whenever the key press event occured.
        if event.key == "q":    # set 'q' key to escape and print lists of data
            plt.close(event.canvas.figure)
            print("\n y1 data list: {}\n".format(self.y1_list))
            print("\n y2 data list: {}\n".format(self.y2_list))

        elif event.key == "d":
            try:
                # remove datapoint from the list
                self.xy_data.x -= 1
                self.x_list.pop(-1)
                self.y1_list.pop(-1)
                self.y2_list.pop(-1)

                # update plot
                self.line1.set_data(self.x_list, self.y1_list)
                self.line1.figure.canvas.draw()
                self.line2.set_data(self.x_list, self.y2_list)
                self.line2.figure.canvas.draw()
            except IndexError:
                print("Empty list")
                self.xy_data.x += 1  # make value x to zero

        else:
            # get current xy plot range. This will be used to update plot range.
            xmin, xmax = self.ax.get_xlim()
            ymin, ymax = self.ax.get_ylim()

            # get x,y data that generated from `xy_data()`
            self.x, self.y1, self.y2 = self.xy_data()

            # Check whether data range exceed the axes limit. If so, change the range.
            if self.x > xmax:
                self.ax.set_xlim(xmin, self.x * 1.5)
            elif self.y1 > ymax:
                self.ax.set_ylim(ymin, abs(self.y1) * 1.1)
            elif self.y2 > ymax:
                self.ax.set_ylim(ymin, abs(self.y2) * 1.1)
            elif self.y1 < ymin:
                self.ax.set_ylim(ymin + self.y1, ymax)
            elif self.y2 < ymin:
                self.ax.set_ylim(ymin + self.y2, ymax)

            # update data list
            self.x_list.append(self.x)
            self.y1_list.append(self.y1)
            self.y2_list.append(self.y2)

            # update plot
            self.line1.set_data(self.x_list, self.y1_list)
            self.line1.figure.canvas.draw()
            self.line2.set_data(self.x_list, self.y2_list)
            self.line2.figure.canvas.draw()

    def PrintOut(self):
        self.filename = input("Input file name without file extencsion: ") + ".xlsx"
        wb = xlw.Workbook("{}".format(self.filename))
        ws = wb.add_worksheet('TDC_mesured result')
        row, col = [0, 0]
        for i in range(len(self.x_list)):
            ws.write(row, col, self.y1_list[i])
            ws.write(row, col + 1, self.y2_list[i])
            row += 1
        wb.close()


if __name__ == '__main__':

    from FindSerial import *
    import time

    arduino = my_serial('Arduino', 9600)
    time.sleep(2)

    data = XY_DataGen(arduino.serialport)
    fig, ax = plt.subplots(figsize=(9, 6))
    tdc_measure = TDC_SpecMeasure(ax, data)
    fig.canvas.mpl_connect("key_press_event", tdc_measure)
    plt.show()
    tdc_measure.PrintOut()
