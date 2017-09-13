# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/AddFacies.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialog_add_facies(object):
    def setupUi(self, dialog_add_facies):
        dialog_add_facies.setObjectName("dialog_add_facies")
        dialog_add_facies.resize(460, 115)
        self.layoutWidget = QtWidgets.QWidget(dialog_add_facies)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 30, 391, 62))
        self.layoutWidget.setObjectName("layoutWidget")
        self.content = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setObjectName("content")
        self.layout_add_facies = QtWidgets.QHBoxLayout()
        self.layout_add_facies.setObjectName("layout_add_facies")
        self.label_new_facies = QtWidgets.QLabel(self.layoutWidget)
        self.label_new_facies.setObjectName("label_new_facies")
        self.layout_add_facies.addWidget(self.label_new_facies)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_add_facies.addItem(spacerItem)
        self.m_edit_new_facies = QtWidgets.QLineEdit(self.layoutWidget)
        self.m_edit_new_facies.setObjectName("m_edit_new_facies")
        self.layout_add_facies.addWidget(self.m_edit_new_facies)
        self.content.addLayout(self.layout_add_facies)
        self.layout_ok_cancle = QtWidgets.QGridLayout()
        self.layout_ok_cancle.setObjectName("layout_ok_cancle")
        self.button_box_ok_cancle = QtWidgets.QDialogButtonBox(self.layoutWidget)
        self.button_box_ok_cancle.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box_ok_cancle.setObjectName("button_box_ok_cancle")
        self.layout_ok_cancle.addWidget(self.button_box_ok_cancle, 0, 1, 1, 1)
        self.m_button_apply = QtWidgets.QPushButton(self.layoutWidget)
        self.m_button_apply.setObjectName("m_button_apply")
        self.layout_ok_cancle.addWidget(self.m_button_apply, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_ok_cancle.addItem(spacerItem1, 0, 0, 1, 1)
        self.content.addLayout(self.layout_ok_cancle)

        self.retranslateUi(dialog_add_facies)
        QtCore.QMetaObject.connectSlotsByName(dialog_add_facies)

    def retranslateUi(self, dialog_add_facies):
        _translate = QtCore.QCoreApplication.translate
        dialog_add_facies.setWindowTitle(_translate("dialog_add_facies", "Dialog"))
        self.label_new_facies.setText(_translate("dialog_add_facies", "New Facies:"))
        self.m_button_apply.setText(_translate("dialog_add_facies", "&Apply"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog_add_facies = QtWidgets.QDialog()
    ui = Ui_dialog_add_facies()
    ui.setupUi(dialog_add_facies)
    dialog_add_facies.show()
    sys.exit(app.exec_())

