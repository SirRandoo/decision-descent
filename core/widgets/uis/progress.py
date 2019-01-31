# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis\progress.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName("ProgressDialog")
        ProgressDialog.resize(276, 93)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/hour-glass-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ProgressDialog.setWindowIcon(icon)
        ProgressDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(ProgressDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.global_progress = QtWidgets.QProgressBar(ProgressDialog)
        self.global_progress.setMaximum(4)
        self.global_progress.setProperty("value", 2)
        self.global_progress.setObjectName("global_progress")
        self.verticalLayout.addWidget(self.global_progress)
        self.local_progress = QtWidgets.QProgressBar(ProgressDialog)
        self.local_progress.setMaximum(3)
        self.local_progress.setProperty("value", 1)
        self.local_progress.setObjectName("local_progress")
        self.verticalLayout.addWidget(self.local_progress)
        self.scope_progress = QtWidgets.QProgressBar(ProgressDialog)
        self.scope_progress.setMaximum(3)
        self.scope_progress.setProperty("value", 1)
        self.scope_progress.setObjectName("scope_progress")
        self.verticalLayout.addWidget(self.scope_progress)
        
        self.retranslateUi(ProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)
    
    def retranslateUi(self, ProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Decision Descent: Client - Progress"))
        self.global_progress.setFormat(_translate("ProgressDialog", "%v/%m"))
        self.local_progress.setFormat(_translate("ProgressDialog", "%v/%m"))
        self.scope_progress.setFormat(_translate("ProgressDialog", "%v/%m"))
