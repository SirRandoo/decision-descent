# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis\info.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_InformationDialog(object):
    def setupUi(self, InformationDialog):
        InformationDialog.setObjectName("InformationDialog")
        InformationDialog.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/write-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        InformationDialog.setWindowIcon(icon)
        InformationDialog.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(InformationDialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pages = QtWidgets.QStackedWidget(InformationDialog)
        self.pages.setObjectName("pages")
        self.text_page = QtWidgets.QWidget()
        self.text_page.setObjectName("text_page")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.text_page)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.text_display = QtWidgets.QTextBrowser(self.text_page)
        self.text_display.setObjectName("text_display")
        self.gridLayout_2.addWidget(self.text_display, 0, 0, 1, 1)
        self.pages.addWidget(self.text_page)
        self.confirmation_page = QtWidgets.QWidget()
        self.confirmation_page.setObjectName("confirmation_page")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.confirmation_page)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.confirmation_no = QtWidgets.QPushButton(self.confirmation_page)
        self.confirmation_no.setObjectName("confirmation_no")
        self.gridLayout_3.addWidget(self.confirmation_no, 1, 2, 1, 1)
        self.confirmation_yes = QtWidgets.QPushButton(self.confirmation_page)
        self.confirmation_yes.setObjectName("confirmation_yes")
        self.gridLayout_3.addWidget(self.confirmation_yes, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 1)
        self.confirmation_display = QtWidgets.QTextBrowser(self.confirmation_page)
        self.confirmation_display.setObjectName("confirmation_display")
        self.gridLayout_3.addWidget(self.confirmation_display, 0, 0, 1, 3)
        self.pages.addWidget(self.confirmation_page)
        self.gridLayout.addWidget(self.pages, 0, 0, 1, 1)
        
        self.retranslateUi(InformationDialog)
        self.pages.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(InformationDialog)
    
    def retranslateUi(self, InformationDialog):
        _translate = QtCore.QCoreApplication.translate
        InformationDialog.setWindowTitle(_translate("InformationDialog", "Decision Descent: Client - Information"))
        self.confirmation_no.setText(_translate("InformationDialog", "Cancel"))
        self.confirmation_yes.setText(_translate("InformationDialog", "OK"))
