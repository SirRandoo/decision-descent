# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'metadata.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MetadataDialog(object):
    def setupUi(self, MetadataDialog):
        MetadataDialog.setObjectName("MetadataDialog")
        MetadataDialog.resize(291, 132)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../assets/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MetadataDialog.setWindowIcon(icon)
        MetadataDialog.setSizeGripEnabled(True)
        self.formLayout = QtWidgets.QFormLayout(MetadataDialog)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setContentsMargins(12, 12, 12, 12)
        self.formLayout.setObjectName("formLayout")
        self.nameLabel = QtWidgets.QLabel(MetadataDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.name = QtWidgets.QLabel(MetadataDialog)
        self.name.setText("")
        self.name.setObjectName("name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name)
        self.versionLabel = QtWidgets.QLabel(MetadataDialog)
        self.versionLabel.setObjectName("versionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.versionLabel)
        self.version = QtWidgets.QLabel(MetadataDialog)
        self.version.setText("")
        self.version.setObjectName("version")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.version)
        self.license_label = QtWidgets.QLabel(MetadataDialog)
        self.license_label.setObjectName("license_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.license_label)
        self.license = QtWidgets.QLabel(MetadataDialog)
        self.license.setText("")
        self.license.setOpenExternalLinks(True)
        self.license.setObjectName("license")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.license)
        self.created_by_label = QtWidgets.QLabel(MetadataDialog)
        self.created_by_label.setObjectName("created_by_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.created_by_label)
        self.created_by = QtWidgets.QLabel(MetadataDialog)
        self.created_by.setText("")
        self.created_by.setObjectName("created_by")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.created_by)
        self.website_label = QtWidgets.QLabel(MetadataDialog)
        self.website_label.setObjectName("website_label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.website_label)
        self.website = QtWidgets.QLabel(MetadataDialog)
        self.website.setText("")
        self.website.setOpenExternalLinks(True)
        self.website.setObjectName("website")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.website)
        self.docs_label = QtWidgets.QLabel(MetadataDialog)
        self.docs_label.setObjectName("docs_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.docs_label)
        self.docs = QtWidgets.QLabel(MetadataDialog)
        self.docs.setText("")
        self.docs.setOpenExternalLinks(True)
        self.docs.setObjectName("docs")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.docs)

        self.retranslateUi(MetadataDialog)
        QtCore.QMetaObject.connectSlotsByName(MetadataDialog)

    def retranslateUi(self, MetadataDialog):
        _translate = QtCore.QCoreApplication.translate
        MetadataDialog.setWindowTitle(_translate("MetadataDialog", "Decision Descent: Client - Metadata"))
        self.nameLabel.setText(_translate("MetadataDialog", "Name"))
        self.versionLabel.setText(_translate("MetadataDialog", "Version"))
        self.license_label.setText(_translate("MetadataDialog", "License"))
        self.created_by_label.setText(_translate("MetadataDialog", "Created By"))
        self.website_label.setText(_translate("MetadataDialog", "Website"))
        self.docs_label.setText(_translate("MetadataDialog", "Docs"))

