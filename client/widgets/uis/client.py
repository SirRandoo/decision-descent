# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis\client.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ClientApp(object):
    def setupUi(self, ClientApp):
        ClientApp.setObjectName("ClientApp")
        ClientApp.resize(571, 407)
        self.app_central = QtWidgets.QWidget(ClientApp)
        self.app_central.setObjectName("app_central")
        self.gridLayout = QtWidgets.QGridLayout(self.app_central)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.log = QtWidgets.QTextBrowser(self.app_central)
        self.log.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.log.setObjectName("log")
        self.gridLayout.addWidget(self.log, 0, 0, 1, 1)
        ClientApp.setCentralWidget(self.app_central)
        self.menu_bar = QtWidgets.QMenuBar(ClientApp)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 571, 21))
        self.menu_bar.setObjectName("menu_bar")
        self.menu_menu = QtWidgets.QMenu(self.menu_bar)
        self.menu_menu.setObjectName("menu_menu")
        self.menu_settings = QtWidgets.QMenu(self.menu_bar)
        self.menu_settings.setObjectName("menu_settings")
        self.menu_help = QtWidgets.QMenu(self.menu_bar)
        self.menu_help.setObjectName("menu_help")
        ClientApp.setMenuBar(self.menu_bar)
        self.menu_quit = QtWidgets.QAction(ClientApp)
        self.menu_quit.setObjectName("menu_quit")
        self.help_about = QtWidgets.QAction(ClientApp)
        self.help_about.setObjectName("help_about")
        self.help_help = QtWidgets.QAction(ClientApp)
        self.help_help.setObjectName("help_help")
        self.help_license = QtWidgets.QAction(ClientApp)
        self.help_license.setShortcut("")
        self.help_license.setObjectName("help_license")
        self.menu_menu.addAction(self.menu_quit)
        self.menu_help.addAction(self.help_help)
        self.menu_help.addAction(self.help_about)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.help_license)
        self.menu_bar.addAction(self.menu_menu.menuAction())
        self.menu_bar.addAction(self.menu_settings.menuAction())
        self.menu_bar.addAction(self.menu_help.menuAction())
        
        self.retranslateUi(ClientApp)
        QtCore.QMetaObject.connectSlotsByName(ClientApp)
    
    def retranslateUi(self, ClientApp):
        _translate = QtCore.QCoreApplication.translate
        ClientApp.setWindowTitle(_translate("ClientApp", "Decision Descent - Client"))
        self.menu_menu.setTitle(_translate("ClientApp", "Menu"))
        self.menu_settings.setTitle(_translate("ClientApp", "Settings"))
        self.menu_help.setTitle(_translate("ClientApp", "Help"))
        self.menu_quit.setText(_translate("ClientApp", "Quit"))
        self.menu_quit.setShortcut(_translate("ClientApp", "Ctrl+Q"))
        self.help_about.setText(_translate("ClientApp", "About"))
        self.help_about.setShortcut(_translate("ClientApp", "Ctrl+A"))
        self.help_help.setText(_translate("ClientApp", "Help"))
        self.help_help.setShortcut(_translate("ClientApp", "Ctrl+H"))
        self.help_license.setText(_translate("ClientApp", "License"))
