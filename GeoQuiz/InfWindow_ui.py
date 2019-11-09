# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InfWindow_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_InfWindow(object):
    def setupUi(self, InfWindow):
        InfWindow.setObjectName("InfWindow")
        InfWindow.resize(400, 300)
        InfWindow.setWindowTitle("")
        InfWindow.setStyleSheet("background-color: hsl(100, 100, 190);")
        self.label_image = QtWidgets.QLabel(InfWindow)
        self.label_image.setGeometry(QtCore.QRect(200, 40, 391, 271))
        self.label_image.setAutoFillBackground(False)
        self.label_image.setText("")
        self.label_image.setObjectName("label_image")
        self.menubar = QtWidgets.QMenuBar(InfWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setStyleSheet("background-color: hsl(100, 10, 210);")
        self.menubar.setDefaultUp(False)
        self.menubar.setObjectName("menubar")
        self.statusbar = QtWidgets.QStatusBar(InfWindow)
        self.statusbar.setObjectName("statusbar")

        self.retranslateUi(InfWindow)
        QtCore.QMetaObject.connectSlotsByName(InfWindow)

    def retranslateUi(self, InfWindow):
        pass
