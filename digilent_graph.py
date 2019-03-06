# -*- coding: utf-8 -*-
"""
This program takes a local .csv file that contains numerical values and graphs
the data. The program should be invoked like so:
$> python digilent_graph.py <path_to_csv>

The csv file is expected to be formatted in a certain way. Each line of the
file chould contain three separated values. The first values is expected to be
time, which is not currently used. The second and third values are data points
for two different channels of data. They will be graphed separately.
"""

from __future__ import print_function
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import csv
import sys
import requests
import socket
import select
import pickle
import time
import os.path
import serial
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import functools

SERIAL_PORT = '/dev/cu.usbmodem14101'
FILE_ID = '1HU_ahCgcivR51r-by7CdfBLhrCdyBnKqaDHfYsEUl0g'


app = QtGui.QApplication([])
layout = pg.LayoutWidget()
op = 0
rate = 1.0
a_data1 = []
a_data2 = []
csv_line_idx = 0
a_p1_op = 0
a_p1_size = 20
a_p2_op = 0
a_p2_size = 20
a_p1 = pg.PlotWidget()
a_p2 = pg.PlotWidget()
ser = serial.Serial(SERIAL_PORT, 19200, timeout=60)  # open serial port at baudrate 19200 with timeout = 1 minute

# def authorize():
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server()
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#     return creds

# def get_data():
#     global ser
#     global csv_line_idx
#     if (not ser.is_open):
#         ser.open()
#     # creds = authorize();
#     # service = build('drive', 'v3', credentials=creds)
#     # try:
#     #     res = service.files().export(fileId=FILE_ID, mimeType='text/csv').execute()
#     # except HttpError, error:
#     #     print(error)
#     line = ser.read(160)
#     if line:
#         items = line.split(',')
#         items.pop()
#         for item in items:
#             try:
#                 print(float(item))
#                 data1.append(float(item))
#             except ValueError:
#                 print("boo")
#             csv_line_idx += 1
    # if res:
    #     for line in res.split('\n'):
    #         items = line.split(',')
    #         if (ptr >= csv_line_idx):
    #             if ptr != 0:
    #                 try:
    #                     data1.append(float(items[1]))
    #                     data2.append(float(items[2]))
    #                 except ValueError:
    #                     print("boo")
    #             csv_line_idx += 1
    #         ptr += 1

# get_data()

# data_timer = QtCore.QTimer()
# data_timer.timeout.connect(get_data)
# data_timer.start(1000)

#print decoded.splitlines()

# with open(sys.argv[1]) as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=',')
#     for line in csv_reader:
#         if csv_line_idx != 0:
#             try:
#                 data1.append(float(line[1]))
#                 data2.append(float(line[2]))
#             except ValueError:
#                 print("boo")
#         csv_line_idx += 1
#     csv_file.close()

def csv_update():
    ptr = 0
    global csv_line_idx
    with open(sys.argv[1]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line in csv_reader:
            if (ptr >= csv_line_idx):
                data1.append(line[1])
                data2.append(line[2])
                csv_line_idx += 1
            ptr += 1
        csv_file.close()

csv_timer = QtCore.QTimer()
csv_timer.timeout.connect(csv_update)
# csv_timer.start(200)

def csv_network():
    ready = ready = select.select([server_socket], [], [], 1)
    if ready[0]:
        message, address = server_socket.recvFrom

def update_op(i):
    global op, ser
    op = i
    ser.write("{}:{}".format(op,rate))

def update_rate(i):
    global rate, ser
    rate = 1 / (10**i)
    ser.write("{}:{}".format(op,rate))

def update_op1(i):
    global a_p1_op
    a_p1_op = i

def update_size1(num):
    global a_p1_size
    a_p1_size = int(num)

def clear_a1():
    a_data1 = []

def update_op2(i):
    global a_p2_op
    a_p2_op = i

def update_size2(num):
    global a_p2_size
    a_p2_size = int(num)

def clear_a2():
    a_data2 = []

#QtGui.QApplication.setGraphicsSystem('raster')

#mw = QtGui.QMainWindow()
#mw.resize(800,800)

#win = pg.GraphicsWindow(title="Basic plotting examples")
#win.resize(1000,600)
#win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)
def ctrl_layout():
    global layout
    label1 = QtGui.QLabel("Acquisition Mode:")
    label2 = QtGui.QLabel("Sampling Rate:")
    operation = QtGui.QComboBox()
    operation.addItems(["Analog"]) # Add DLA later?
    operation.currentIndexChanged.connect(update_op)
    rate = QtGui.QComboBox()
    rate.addItems(["1 samples / 1 s", "1 samples / 100 ms", "1 samples / 10 ms", "1 samples / 1 ms", "1 samples / 100 us"])
    rate.currentIndexChanged.connect(update_rate)
    layout.addWidget(label1, row=0, col=0)
    layout.addWidget(operation, row=0, col=1)
    layout.addWidget(label2, row=0, col=2)
    layout.addWidget(rate, row=0, col=3)

def analog_layout():
    global layout, a_p1, a_p2
    # Probe 1 layout
    label1 = QtGui.QLabel("Analog Probe 1")
    label2 = QtGui.QLabel("Plotting Style:")
    label3 = QtGui.QLabel("Samples in Window:")
    clear1 = QtGui.QPushButton("Clear Data")
    clear1.clicked.connect(clear_a1)
    g1_operation = QtGui.QComboBox()
    g1_operation.addItems(["Expanding Window", "Fixed Window"])
    g1_operation.currentIndexChanged.connect(update_op1)
    g1_win_size = QtGui.QLineEdit(displayText='Points in Window:', text='20')
    g1_win_size.textChanged.connect(update_size1)
    a_p1 = pg.PlotWidget()
    layout.addWidget(label1, row=1, col=0)
    layout.addWidget(label2, row=1, col=1)
    layout.addWidget(g1_operation, row=1, col=2)
    layout.addWidget(label3, row=1, col=3)
    layout.addWidget(g1_win_size, row=1, col=4)
    layout.addWidget(clear1, row=1, col=5)
    layout.addWidget(a_p1, row=2, col=0, colspan=6)
    # Probe 2 layout
    label4 = QtGui.QLabel("Analog Probe 2")
    label5 = QtGui.QLabel("Plotting Style:")
    label6 = QtGui.QLabel("Samples in Window:")
    clear2 = QtGui.QPushButton("Clear Data")
    clear1.clicked.connect(clear_a2)
    g2_operation = QtGui.QComboBox()
    g2_operation.addItems(["Expanding Window", "Fixed Window"])
    g2_operation.currentIndexChanged.connect(update_op2)
    g2_win_size = QtGui.QLineEdit(displayText='Points in Window:', text='20')
    g2_win_size.textChanged.connect(update_size2)
    a_p2 = pg.PlotWidget()
    layout.addWidget(label4, row=3, col=0)
    layout.addWidget(label5, row=3, col=1)
    layout.addWidget(g2_operation, row=3, col=2)
    layout.addWidget(label6, row=3, col=3)
    layout.addWidget(g2_win_size, row=3, col=4)
    layout.addWidget(clear2, row=3, col=5)
    layout.addWidget(a_p2, row=4, col=0, colspan=6)
    # Add all items to the window
    layout.resize(800,800)
    layout.show()

#p1.plot(title="Basic array plotting", y=np.random.normal(size=100))

#p2 = win.addPlot(title="Updating plot")



def update1():
    global curve1, ptr1, a_p1, a_data1
    if (a_p1_op == 0):
        curve1.setData(a_data1)
    else:
        curve1.setData(a_data1[csv_line_idx-a_p1_size:])


def update2():
    global curve2, ptr2, p2, data2
    if (p2_op == 0):
        curve2.setData(data2)
    else:
        curve2.setData(data2[csv_line_idx-p2_size:])

# Actually start running things here:
ctrl_layout()
analog_layout()

# Start analog probe 1 update events
curve1 = a_p1.plot(pen='y')
timer1 = QtCore.QTimer()
timer1.timeout.connect(update1)
timer1.start(rate*1000)

# Start analog probe 2 update events
curve2 = p2.plot(pen='y')
timer2 = QtCore.QTimer()
timer2.timeout.connect(update2)
timer2.start(rate*1000)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
