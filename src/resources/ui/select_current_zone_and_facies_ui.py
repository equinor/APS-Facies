# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/select_current_zone_and_facies.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_select_zone_and_facies(object):
    def setupUi(self, select_zone_and_facies):
        select_zone_and_facies.setObjectName("select_zone_and_facies")
        select_zone_and_facies.setWindowModality(QtCore.Qt.NonModal)
        select_zone_and_facies.resize(781, 226)
        self.layoutWidget = QtWidgets.QWidget(select_zone_and_facies)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 775, 217))
        self.layoutWidget.setObjectName("layoutWidget")
        self.layout_select_zones_and_facies = QtWidgets.QGridLayout(self.layoutWidget)
        self.layout_select_zones_and_facies.setContentsMargins(0, 0, 0, 0)
        self.layout_select_zones_and_facies.setObjectName("layout_select_zones_and_facies")
        self.label_select_current_zone_and_facies = QtWidgets.QLabel(self.layoutWidget)
        self.label_select_current_zone_and_facies.setWordWrap(True)
        self.label_select_current_zone_and_facies.setObjectName("label_select_current_zone_and_facies")
        self.layout_select_zones_and_facies.addWidget(self.label_select_current_zone_and_facies, 1, 0, 1, 1)
        self.label_select_facies = QtWidgets.QLabel(self.layoutWidget)
        self.label_select_facies.setObjectName("label_select_facies")
        self.layout_select_zones_and_facies.addWidget(self.label_select_facies, 0, 3, 1, 1)
        self.m_list_facies = QtWidgets.QListWidget(self.layoutWidget)
        self.m_list_facies.setObjectName("m_list_facies")
        self.layout_select_zones_and_facies.addWidget(self.m_list_facies, 1, 3, 1, 1)
        self.label_select_zones = QtWidgets.QLabel(self.layoutWidget)
        self.label_select_zones.setObjectName("label_select_zones")
        self.layout_select_zones_and_facies.addWidget(self.label_select_zones, 0, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.m_button_remove_zone = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_button_remove_zone.sizePolicy().hasHeightForWidth())
        self.m_button_remove_zone.setSizePolicy(sizePolicy)
        self.m_button_remove_zone.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.m_button_remove_zone.setFont(font)
        self.m_button_remove_zone.setIconSize(QtCore.QSize(16, 16))
        self.m_button_remove_zone.setObjectName("m_button_remove_zone")
        self.verticalLayout.addWidget(self.m_button_remove_zone)
        self.m_button_add_zone = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.m_button_add_zone.sizePolicy().hasHeightForWidth())
        self.m_button_add_zone.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.m_button_add_zone.setFont(font)
        self.m_button_add_zone.setObjectName("m_button_add_zone")
        self.verticalLayout.addWidget(self.m_button_add_zone)
        self.layout_select_zones_and_facies.addLayout(self.verticalLayout, 1, 2, 1, 1)
        self.m_list_zones = QtWidgets.QListWidget(self.layoutWidget)
        self.m_list_zones.setObjectName("m_list_zones")
        self.layout_select_zones_and_facies.addWidget(self.m_list_zones, 1, 1, 1, 1)

        self.retranslateUi(select_zone_and_facies)
        QtCore.QMetaObject.connectSlotsByName(select_zone_and_facies)

    def retranslateUi(self, select_zone_and_facies):
        _translate = QtCore.QCoreApplication.translate
        select_zone_and_facies.setWindowTitle(_translate("select_zone_and_facies", "Select current zone and facies"))
        self.label_select_current_zone_and_facies.setText(_translate("select_zone_and_facies", "Select current zone and facies"))
        self.label_select_facies.setText(_translate("select_zone_and_facies", "Selected Facies"))
        self.label_select_zones.setText(_translate("select_zone_and_facies", "Zones selection"))
        self.m_button_remove_zone.setText(_translate("select_zone_and_facies", ">"))
        self.m_button_add_zone.setText(_translate("select_zone_and_facies", "<"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    select_zone_and_facies = QtWidgets.QWidget()
    ui = Ui_select_zone_and_facies()
    ui.setupUi(select_zone_and_facies)
    select_zone_and_facies.show()
    sys.exit(app.exec_())

