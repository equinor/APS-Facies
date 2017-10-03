from src.gui.state import State
from src.gui.wrappers.base_classes.truncation import BaseTruncation
from src.resources.ui.TruncRuleCubic_ui import Ui_CubicTruncationRule
from src.resources.ui.TruncRuleTypeNonCubic_ui import Ui_NonCubicTruncationRule
from src.resources.ui.TruncRuleTypeBayfill_ui import Ui_BayfillTruncationRule
from src.utils.constants import Defaults, BaseNames


class CubicTruncationRule(BaseTruncation, Ui_CubicTruncationRule):
    def __init__(
            self,
            state: State,
            parent=None,
            name_of_buttons=Defaults.NAME_OF_BUTTON_BOX,
            basename_sliders=Defaults.NAME_OF_SLIDERS,
            basename_proportions=Defaults.NAME_OF_PROPORTIONS,
            active=None
    ):
        super(CubicTruncationRule, self).__init__(
            parent=parent,
            state=state,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            active=active
        )
        self.setupUi(self)
        self.retranslateUi(self)
        self.active = ['F1', 'F2', 'F3', 'F4']  # TODO: Should be removed, in favor of dynamically loading

        self.wire_up()


class NonCubicTruncationRule(BaseTruncation, Ui_NonCubicTruncationRule):
    def __init__(
            self,
            state: State,
            parent=None,
            name_of_buttons=Defaults.NAME_OF_BUTTON_BOX,
            basename_sliders=Defaults.NAME_OF_SLIDERS,
            basename_proportions=Defaults.NAME_OF_PROPORTIONS,
            basename_angles=Defaults.NAME_OF_ANGLES,
            active=None
    ):
        super(NonCubicTruncationRule, self).__init__(
            parent=parent,
            state=state,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            active=active
        )
        self.setupUi(self)
        self.retranslateUi(self)
        self.active = ['F1', 'F2', 'F3', 'F4']  # TODO: Should be removed, in favor of dynamically loading
        self._set_base_names(BaseNames.ANGLES, basename_angles)

        self.wire_up()


class BayfillTruncationRule(BaseTruncation, Ui_BayfillTruncationRule):
    def __init__(
            self,
            state: State,
            parent=None,
            name_of_buttons=Defaults.NAME_OF_BUTTON_BOX,
            basename_sliders=Defaults.NAME_OF_SLIDERS,
            basename_proportions=Defaults.NAME_OF_PROPORTIONS,
            basename_slanted_factor=Defaults.NAME_OF_SLANTED_FACTOR,
    ):
        super(BayfillTruncationRule, self).__init__(
            parent=parent,
            state=state,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            names=['floodplain', 'subbay', 'WBF', 'BHD', 'lagoon'],
            active=['floodplain', 'subbay', 'WBF', 'BHD', 'lagoon']
        )
        self.setupUi(self)
        self.retranslateUi(self)
        self._set_base_names(BaseNames.SLANT_FACTOR, basename_slanted_factor)

        self.wire_up()
