from typing import List, Callable, Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from src.resources.ui.TruncRuleCubic_ui import Ui_CubicTruncationRule
from src.utils.constants import Proportions
from src.gui.wrappers.base_classes import BaseTruncation


class CubicTruncationRule(BaseTruncation, Ui_CubicTruncationRule):
    def __init__(self, parent=None):
        super(CubicTruncationRule, self).__init__(parent=parent)
        self.setupUi(self)
        self.retranslateUi(self)

        self.wire_up()

        pass

    def wire_up(self):
        validator = QDoubleValidator(bottom=Proportions.BOTTOM, top=Proportions.TOP, decimals=Proportions.DECIMALS)
        proportion_inputs = [self.__getattribute__('m_edit_proportion_' + name) for name in self.names]
        sliders = [self.__getattribute__('m_slider_' + name) for name in self.names]

        # Set edits fields to be numbers only
        self.apply_method_to(proportion_inputs, lambda x: x.setValidator(validator))

        for i in range(len(self.names)):
            slider = sliders[i]  # type: QSlider
            line_edit = proportion_inputs[i]  # type: QLineEdit
            self.connect_slider_and_text(slider, line_edit)

        # self.m_edit_proportion_F1.textChanged.connect(self.calculate_sums)
        pass
