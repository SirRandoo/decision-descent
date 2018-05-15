# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis\auth.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AuthScreen(object):
    def setupUi(self, AuthScreen):
        AuthScreen.setObjectName("AuthScreen")
        AuthScreen.resize(575, 408)
        AuthScreen.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(AuthScreen)
        self.gridLayout.setObjectName("gridLayout")
        self.View = QtWebEngineWidgets.QWebEngineView(AuthScreen)
        self.View.setObjectName("View")
        self.gridLayout.addWidget(self.View, 0, 0, 1, 1)
        
        self.retranslateUi(AuthScreen)
        QtCore.QMetaObject.connectSlotsByName(AuthScreen)
    
    def retranslateUi(self, AuthScreen):
        _translate = QtCore.QCoreApplication.translate
        AuthScreen.setWindowTitle(_translate("AuthScreen", "Authentication Screen"))


from PyQt5 import QtWebEngineWidgets
