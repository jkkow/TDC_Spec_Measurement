"""
This class reads measured data from device and return the data set whenever it is called.
The data comes from Aruduino Uno board that connected
to Dual channel powermeter. The Aruduino emits two line of data at a
time, one line for chennel 1 and the other for channel 2.

Author: jkkow
Created: 2017-11-08T02:46:52
"""
import matplotlib.pyplot as plt
import xlsxwriter as xlw    # library for handling Excel file.
import numpy as np


class get_dataGen(object):

    def __init__(self, device):
        # get `serial` instance from device that is connected via serial
        # communication. If you use customized `FindSerial` class, make sure to use the
        # device instace as like `deviceintstace.serialport`.
        self.device = device
        self.x = 0  # set start value as zero for mesurement steps

    def __call__(self):
        self.x += 1  # increase measurement step
        self.device.write('r'.encode())
        self.y1 = int(self.device.readline().decode())  # read data y1 from the device
        self.y2 = int(self.device.readline().decode())
        self.sum = self.y1 + self.y2

        return [self.x, self.y1, self.y2, self.sum]


class TDC_SpecMeasure(object):
    def __init__(self, ax, data):
        # Core role of this __init_() function is intializing the graph configuration.
        self.ax = ax  # get 'ax' object
        self.get_data = data  # get a function that returns measured data values as initial parameter

        self.ax.set_title("TDC Examination", fontsize=15)
        self.ax.set_xlabel("Dial Ticks", fontsize=13, labelpad=12)
        self.ax.set_ylabel("Power(A.U.)", fontsize=13, labelpad=12)
        # self.ax.set_yticklabels([])

        self.xmin_init, self.xmax_init = 0, 10  # set initial xmin, xmax for plot range
        self.ymin_init, self.ymax_init = -0.2, 1.1  # set initial ymin, ymax for plot range
        # axes range setting
        self.ax.set_xlim(self.xmin_init, self.xmax_init)
        self.ax.set_ylim(self.ymin_init, self.ymax_init)

        # make empty array for measured data and summed result
        self.x_list, self.y1_list, self.y2_list = [], [], []
        self.sum_arr = np.array([])

        # intial plot line1 for data y1
        self.line1, = self.ax.plot(self.x_list, self.y1_list, '-o', label="Ch_1")
        # initila plot line2 for data y2
        self.line2, = self.ax.plot(self.x_list, self.y2_list, '-x', label="Ch_2")
        # initial plotline3 for summation result of y1 and y2
        self.line3, = self.ax.plot(self.x_list, self.sum_arr, '-d', label="Total")
        self.ax.legend(loc=0, fontsize=12)

    def __call__(self, event):
        # This magic method is called whenever the key press event occured.
        if event.key == "q":    # set 'q' key to escape and print lists of data
            plt.close(event.canvas.figure)
            print("\n x data list: {}\n".format(self.x_list))
            print("\n y1 data list: {}\n".format(self.y1_list))
            print("\n y2 data list: {}\n".format(self.y2_list))
            print("\n summed data: {}\n".format(self.sum_arr))

        elif event.key == 'backspace' or event.key == 'd' or event.key == 'left':
            try:
                print(event.key)
                # remove datapoint from the list
                self.get_data.x -= 1  # one step back of index x
                # pop out last value in the array
                self.x_list.pop(-1)
                self.y1_list.pop(-1)
                self.y2_list.pop(-1)
                self.sum_arr = self.sum_arr[:-1]

                self.Check_PlotRange('deliting')

                # update plot
                self.line1.set_data(self.x_list, self.y1_list)
                self.line2.set_data(self.x_list, self.y2_list)
                self.line3.set_data(self.x_list, self.sum_arr)
                self.ax.figure.canvas.draw()

            except IndexError:
                print("Empty list")
                self.get_data.x += 1  # reset x to zero

        elif event.key == ' ' or event.key == 'enter' or event.key == 'right':
            # get x,y data that generated from `get_data()`
            print("The key '{}' is pressed".format(event.key))
            self.x, self.y1, self.y2, self.sum = self.get_data()

            # update data list
            self.x_list.append(self.x)
            self.y1_list.append(self.y1)
            self.y2_list.append(self.y2)
            # append summed result of y1 and y2 to sum_arr
            self.sum_arr = np.append(self.sum_arr, self.sum)

            # Check whether data range exceed the plot range. If so, change the range.
            self.Check_PlotRange('adding')

            # update plot
            self.line1.set_data(self.x_list, self.y1_list)
            self.line2.set_data(self.x_list, self.y2_list)
            self.line3.set_data(self.x_list, self.sum_arr)
            self.ax.figure.canvas.draw()

        else:
            print("\n\tYou've press '{}' key.".format(event.key))
            print("\tTo add point: type 'enter' or 'spacebar' or 'right'.\n\tTo delete point: type 'd' or 'backspace' or 'left'")

    def Check_PlotRange(self, plot_mode):

        self.xmin, self.xmax = self.ax.get_xlim()
        self.ymin, self.ymax = self.ax.get_ylim()
        # maximum value among the data
        topval = max([max(self.y1_list), max(self.y2_list), max(self.sum_arr)])
        # minimum value among thd data
        botval = min([min(self.y1_list), min(self.y2_list), min(self.sum_arr)])

        if plot_mode == "deliting":  # the case when 'd' key pressed
            if (self.ymax - topval) > 0.1 * abs(topval):
                self.ax.set_ylim(self.ymin, topval + 0.2 * abs(topval))
                self.ymin, self.ymax = self.ax.get_ylim()
            if (botval - self.ymin) > 0.1 * botval:
                self.ax.set_ylim(botval - 0.1 * abs(botval), self.ymax)
                self.ymin, self.ymax = self.ax.get_ylim()

        elif plot_mode == "adding":  # the case when a key pressed
            if self.x > self.xmax:
                self.ax.set_xlim(self.xmin, self.x + 50)
            if topval > self.ymax:
                self.ax.set_ylim(self.ymin, topval * 1.2)
                self.ymin, self.ymax = self.ax.get_ylim()
            if botval < self.ymin:
                self.ax.set_ylim(botval - 0.2 * abs(botval), self.ymax)
                self.ymin, self.ymax = self.ax.get_ylim()

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

    data = get_dataGen(arduino.serialport)
    fig, ax = plt.subplots(figsize=(9, 6))
    tdc_measure = TDC_SpecMeasure(ax, data)
    fig.canvas.mpl_connect("key_press_event", tdc_measure)
    plt.show()
    tdc_measure.PrintOut()
