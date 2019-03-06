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

data1 = []
data2 = []
csv_line_idx = 0
p1_op = 0
p1_size = 20
p2_op = 0
p2_size = 20
ser = serial.Serial(SERIAL_PORT, 19200, timeout=60)  # open serial port at baudrate 19200 with timeout = 1 minute
app = QtGui.QApplication([])

def authorize():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_data():
    global ser
    global csv_line_idx
    if (not ser.is_open):
        ser.open()
    # creds = authorize();
    # service = build('drive', 'v3', credentials=creds)
    # try:
    #     res = service.files().export(fileId=FILE_ID, mimeType='text/csv').execute()
    # except HttpError, error:
    #     print(error)
    line = ser.read(160)
    if line:
        items = line.split(',')
        items.pop()
        for item in items:
            try:
                print(float(item))
                data1.append(float(item))
            except ValueError:
                print("boo")
            csv_line_idx += 1
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

data_timer = QtCore.QTimer()
data_timer.timeout.connect(get_data)
data_timer.start(1000)

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


def update_op1(i):
    global p1_op
    p1_op = i

def update_size1(num):
    global p1_size
    p1_size = int(num)

def update_op2(i):
    global p2_op
    p2_op = i

def update_size2(num):
    global p2_size
    p2_size = int(num)

#QtGui.QApplication.setGraphicsSystem('raster')

#mw = QtGui.QMainWindow()
#mw.resize(800,800)

#win = pg.GraphicsWindow(title="Basic plotting examples")
#win.resize(1000,600)
#win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

label1 = QtGui.QLabel("Analog Probe 1")
g1_operation = QtGui.QComboBox()
g1_operation.addItems(["Expanding Window", "Fixed Window"])
g1_operation.currentIndexChanged.connect(update_op1)
g1_win_size = QtGui.QLineEdit(displayText='Points in Window:', text='20')
g1_win_size.textChanged.connect(update_size1)
label2 = QtGui.QLabel("Analog Probe 2")
g2_operation = QtGui.QComboBox()
g2_operation.addItems(["Expanding Window", "Fixed Window"])
g2_operation.currentIndexChanged.connect(update_op2)
g2_win_size = QtGui.QLineEdit(displayText='Points in Window:', text='20')
g2_win_size.textChanged.connect(update_size2)
layout = pg.LayoutWidget()
p1 = pg.PlotWidget()
p2 = pg.PlotWidget()
layout.addWidget(label1, row=0, col=0)
layout.addWidget(g1_operation, row=0, col=1)
layout.addWidget(g1_win_size, row=0, col=2)
layout.addWidget(p1, row=1, col=0, colspan=3)
layout.addWidget(label2, row=2, col=0)
layout.addWidget(g2_operation, row=2, col=1)
layout.addWidget(g2_win_size, row=2, col=2)
layout.addWidget(p2, row=3, col=0, colspan=3)
layout.resize(800,800)
layout.show()

#p1.plot(title="Basic array plotting", y=np.random.normal(size=100))

#p2 = win.addPlot(title="Updating plot")



curve1 = p1.plot(pen='y')
ptr1 = 0
def update1():
    global curve1, ptr1, p1, data1
    if (p1_op == 0):
        curve1.setData(data1)
    else:
        curve1.setData(data1[csv_line_idx-p1_size:])
timer1 = QtCore.QTimer()
timer1.timeout.connect(update1)
timer1.start(200)

# curve2 = p2.plot(pen='y')
# ptr2 = 0
# def update2():
#     global curve2, ptr2, p2, data2
#     if (p2_op == 0):
#         curve2.setData(data2)
#     else:
#         curve2.setData(data2[csv_line_idx-p2_size:])
# timer2 = QtCore.QTimer()
# timer2.timeout.connect(update2)
# timer2.start(200)



#win.nextRow()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
