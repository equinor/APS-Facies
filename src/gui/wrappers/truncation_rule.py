from src.gui.state import State
from src.gui.wrappers.base_classes.truncation import BaseTruncation
from src.resources.ui.TruncRuleCubic_ui import Ui_CubicTruncationRule
from src.resources.ui.TruncRuleTypeBayfill_ui import Ui_BayfillTruncationRule
from src.resources.ui.TruncRuleTypeNonCubic_ui import Ui_NonCubicTruncationRule
from src.utils.constants import BaseNames, Defaults


class CubicTruncationRule(BaseTruncation, Ui_CubicTruncationRule):
    def __init__(
            self,
            state: State,
            parent=None,
            name_of_buttons=Defaults.NAME_OF_BUTTON_BOX,
            basename_sliders=Defaults.NAME_OF_SLIDERS,
            basename_proportions=Defaults.NAME_OF_PROPORTIONS,
            facies_options=None,
            color_options=None,
            active=None
    ):
        super(CubicTruncationRule, self).__init__(
            parent=parent,
            state=state,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            facies_options=facies_options,
            color_options=color_options,
            active=active
        )
        self.setupUi(self)
        self.retranslateUi(self)

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
            facies_options=None,
            color_options=None,
            active=None
    ):
        super(NonCubicTruncationRule, self).__init__(
            parent=parent,
            state=state,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            facies_options=facies_options,
            color_options=color_options,
            active=active
        )
        self.setupUi(self)
        self.retranslateUi(self)
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
            facies_options=None,
            color_options=None,
    ):
        super(BayfillTruncationRule, self).__init__(
            parent=parent,
            state=state,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            facies_options=facies_options,
            color_options=color_options,
            names=['floodplain', 'subbay', 'WBF', 'BHD', 'lagoon'],
            active=['floodplain', 'subbay', 'WBF', 'BHD', 'lagoon']
        )
        self.setupUi(self)
        self.retranslateUi(self)
        self._set_base_names(BaseNames.SLANT_FACTOR, basename_slanted_factor)

        self.wire_up()


class CustomTruncationRule(BaseTruncation):
    # TODO: Implement
    def __init__(
            self,
            state: State,
            parent=None,
            name_of_buttons=Defaults.NAME_OF_BUTTON_BOX,
            basename_sliders=Defaults.NAME_OF_SLIDERS,
            basename_proportions=Defaults.NAME_OF_PROPORTIONS,
            basename_color_button=Defaults.NAME_OF_COLOR_BUTTON,
            basename_drop_down=Defaults.NAME_OF_DROP_DOWN,
            facies_options=None,
            color_options=None,
            names=None,
            active=None
    ):
        super(CustomTruncationRule, self).__init__(
            state=state,
            parent=parent,
            name_of_buttons=name_of_buttons,
            basename_sliders=basename_sliders,
            basename_proportions=basename_proportions,
            basename_color_button=basename_color_button,
            basename_drop_down=basename_drop_down,
            facies_options=facies_options,
            color_options=color_options,
            names=names,
            active=active
        )
        pass
