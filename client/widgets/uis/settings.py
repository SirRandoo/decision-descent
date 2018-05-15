# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis\settings.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DDSettings(object):
    def setupUi(self, DDSettings):
        DDSettings.setObjectName("DDSettings")
        DDSettings.resize(486, 345)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/write-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DDSettings.setWindowIcon(icon)
        DDSettings.setSizeGripEnabled(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(DDSettings)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.overview_widget = QtWidgets.QWidget(DDSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.overview_widget.sizePolicy().hasHeightForWidth())
        self.overview_widget.setSizePolicy(sizePolicy)
        self.overview_widget.setMaximumSize(QtCore.QSize(150, 16777215))
        self.overview_widget.setObjectName("overview_widget")
        self.gridLayout = QtWidgets.QGridLayout(self.overview_widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.query = QtWidgets.QLineEdit(self.overview_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.query.sizePolicy().hasHeightForWidth())
        self.query.setSizePolicy(sizePolicy)
        self.query.setClearButtonEnabled(True)
        self.query.setObjectName("query")
        self.gridLayout.addWidget(self.query, 0, 0, 1, 1)
        self.overview = QtWidgets.QTreeWidget(self.overview_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.overview.sizePolicy().hasHeightForWidth())
        self.overview.setSizePolicy(sizePolicy)
        self.overview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.overview.setTabKeyNavigation(True)
        self.overview.setProperty("showDropIndicator", False)
        self.overview.setIndentation(10)
        self.overview.setAnimated(True)
        self.overview.setWordWrap(True)
        self.overview.setObjectName("overview")
        self.overview.headerItem().setText(0, "1")
        self.overview.header().setVisible(False)
        self.gridLayout.addWidget(self.overview, 1, 0, 1, 1)
        self.horizontalLayout.addWidget(self.overview_widget)
        self.settings_area = QtWidgets.QStackedWidget(DDSettings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_area.sizePolicy().hasHeightForWidth())
        self.settings_area.setSizePolicy(sizePolicy)
        self.settings_area.setObjectName("settings_area")
        self.horizontalLayout.addWidget(self.settings_area)
        
        self.retranslateUi(DDSettings)
        QtCore.QMetaObject.connectSlotsByName(DDSettings)
    
    def retranslateUi(self, DDSettings):
        _translate = QtCore.QCoreApplication.translate
        DDSettings.setWindowTitle(_translate("DDSettings", "Decision Descent - Settings"))
