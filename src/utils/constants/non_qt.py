from src.utils.constants.base import Key, Value

# TODO: Implement automatic initialization, when accessing a constant
# Ex. ProjectConstants.PATH_OF_PROJECT_FIL (with, or without () at the end) will give a class instance having that value


class DataBase(Value):
    NAME = 'state.db'


class DrawingLibrary(Value):
    LIBRARY_FOLDER = ''  # Set automatically by make
    NAME = 'libdraw2D.so'
    LIBRARY_PATH = LIBRARY_FOLDER + '/' + NAME


class ModeConstants(Key):
    EXECUTION_MODE = 'execution mode'


class ModeOptions(Value):
    READING_MODE = 'reading'
    EXPERIMENTAL_MODE = 'experimental'


class ProjectConstants(Key):
    PATH_OF_PROJECT_FILE = 'path of project file'
    WORKFLOW_NAME = 'workflow name'
    FACIES_PARAMETER_NAME = 'facies parameter name'
    GAUSSIAN_PARAMETER_NAME = 'gaussian parameter name'
    GRID_MODEL_NAME = 'grid model name'
    ZONES_PARAMETER_NAME = 'zone parameter name'


class ProjectElements(Value):
    BROWSE_PROJECT_BUTTON = 'm_button_browse_project_file'
    BROWSE_PROJECT_INPUT = 'm_edit_browse_project'
    EXPERIMENTAL_BUTTON = 'm_rb_experimental_mode'
    FACIES_PARAMETER_NAME = 'm_edit_facies_parameter_name'
    GAUSSIAN_PARAMETER_NAME = 'm_edit_gaussian_parameter_name'
    GRID_MODEL_NAME = 'm_edit_grid_model_name'
    READ_PROJECT_FILE = 'm_rb_read_rms_project_file'
    WORKFLOW_NAME = 'm_edit_workflow_name'
    ZONES_PARAMETER_NAME = 'm_edit_zones_parameter_name'


class AddFaciesElements(Value):
    NEW_FACIES_NAME = 'm_edit_new_facies'


class MainWindowConstants(Key):
    pass


class MainWindowElements(Value):
    ASSIGN_PROBABILITY_CUBE = 'm_button_assign_probability'
    CLOSE = 'm_button_close'
    CONDITION_TO_WELL = 'm_toggle_condition_to_wells'
    EXPERIMENTAL_MODE = 'm_toggle_experimental_mode'
    RUN_PREVIEWER = 'm_button_previewer'
    SAVE = 'm_button_save'
    SAVE_AS = 'm_button_save_as'


class OutputFaciesModelNameElements(MainWindowElements):
    TITLE = 'label_model_name'
    SELECT_FACIES_MODEL = 'm_choose_select_facies_model'
    MODEL_NAME = 'm_edit_model_name'

    # Labels
    LABEL_SELECT_FACIES_MODEL = 'label_select_facies_model'
    LABEL_MODEL_NAME = 'label_create'


class ZoneSelectionElements(MainWindowElements):
    # Button for making the elements interactive
    TOGGLE = 'm_toggle_separate_zone_models'
    # Lists for available and selected
    AVAILABLE = 'm_list_available_zones'
    SELECTED = 'm_list_selected_zones'
    # Buttons for moving items from 'selectable' to being 'selected'
    SELECT = 'm_button_add_zone'
    UNSELECT = 'm_button_remove_zone'

    # Labels
    LABEL_TITLE = 'label_zones_to_be_modeled'
    LABEL_AVAILABLE = 'label_available_zones'
    LABEL_SELECTED = 'label_selected_zones'


class RegionSelectionElements(MainWindowElements):
    pass


class FaciesSelectionElements(MainWindowElements):
    # Button for making the elements interactive
    TOGGLE = 'm_toggle_select_facies'
    # Lists for available and selected
    AVAILABLE = 'm_list_available_facies'
    SELECTED = 'm_list_selected_facies'
    # Buttons for moving items from 'selectable' to being 'selected'
    SELECT = 'm_button_add_facies'
    UNSELECT = 'm_button_remove_facies'
    # Buttons for adding, and removing additional facies
    ADD_FACIES = 'm_button_add_new_facies'
    REMOVE_FACIES = 'm_button_remove_selected'

    # Labels
    LABEL_TITLE = 'label_facies_to_be_modelled'
    LABEL_AVAILABLE = 'label_available_facies'
    LABEL_SELECTED = 'label_selected_facies'


class FaciesSelectionConstants(Key):
    AVAILABLE = 'available facies'
    SELECTED = 'selected facies'


class TruncationRuleLibraryElements(MainWindowElements):
    CUBIC_BUTTON = 'm_button_type_'
    NON_CUBIC_BUTTON = 'm_button_type_'
    BAYFILL_BUTTON = 'm_button_bayfill'
    CUSTOM_BUTTON = 'm_button_type_customized'
    ZONES = 'm_list_zones'
    FACIES = 'm_list_facies'


class GaussianRandomFieldElements(MainWindowElements):
    NUMBER_OF_ELEMENTS = 6
    PLOT_AREA = 'm_plot_area_'
    SETTINGS = 'm_button_settings_'
    APPLY = 'm_toggle_'
    ZONES = 'm_list_zones_grf'
    FACIES = 'm_list_facies_grf'


class GaussianRandomFieldConstants(Key):
    AVAILABLE = 'available grf models'
    SELECTED = 'selected grf models'
    CURRENT = 'currently selected grf model'


class DefineGaussianElements(Value):
    TOGGLE_TREND = 'm_toggle_apply_trend'


class VariogramModelElements(DefineGaussianElements):
    VARIOGRAM = 'm_choose_variogram_model'
    AZIMUTH = 'm_edit_azimuth'
    DIP = 'm_edit_dip'
    PARALLEL = 'm_edit_parallel_to_azimuth'
    NORMAL = 'm_edit_normal_to_azimuth'
    VERTICAL = 'm_edit_vertical_normal_to_dip'
    PLOT = 'm_plot_variogram'
    POWER = 'm_edit_power'

    # Labels
    LABEL_POWER = 'label_power'


class VariogramModelConstants(Key):
    VARIOGRAM = 'variogram model'
    AZIMUTH = 'azimuth angle'
    DIP = 'dip angle'
    PARALLEL = 'parallel to azimuth'
    NORMAL = 'normal to azimuth'
    VERTICAL = 'vertical normal to dip'
    POWER = 'power'


class TrendSettingsElements(DefineGaussianElements):
    TREND = 'm_choose_select_trend'
    DEPOSITIONAL_DIRECTION = 'm_edit_depositional_direction'
    STACKING_PATTERN = 'm_choose_stacking_pattern'
    STACKING_ANGLE = 'm_edit_stacking_angle'
    RELATIVE_STANDARD_DEVIATION = 'm_edit_relative_standard_deviation'
    SIMULATION_BOX_THICKNESS = 'm_edit_simbox_thickness'
    PLOT = 'm_plot_trend'


class TrendSettingsLabelsElements(TrendSettingsElements):
    TITLE = 'label_trend_settings'
    SELECT_TREND = 'label_select_trend'
    DEPOSITIONAL_DIRECTION_LABEL = 'label_depositional_direction'
    STACKING_PATTERN_LABEL = 'label_stacking_pattern'
    STACKING_ANGLE_LABEL = 'label_stacking_angle'
    RELATIVE_STANDARD_DEVIATION_LABEL = 'label_relative_standard_deviation'
    SIMULATION_BOX_THICKNESS_LABEL = 'label_simbox_thickness'


class BaseNames(Value):
    ANGLES = 'basename_angles'
    COLOR_BUTTON = 'basename_color_button'
    DROP_DOWN = 'basename_drop_down'
    SLIDERS = 'basename_sliders'
    PROPORTIONS = 'basename_proportions'
    SLANT_FACTOR = 'basename_slanted_factor'


class TruncationLibrary(Key):
    pass


class TruncationLibraryKeys(TruncationLibrary):
    KEY = 'truncation rule type'
    # Keys for types of truncation rules
    CUBIC = 'cubic'
    NON_CUBIC = 'non-cubic'
    BAYFILL = 'bayfill'
    CUSTOM = 'custom'


class TruncationLibrarySubKeys(TruncationLibrary):
    # Keys used in the library mapping
    NUMBER_OF_FACIES_KEY = 'number of facies'
    BUTTON_NAME_KEY = 'button name, or prefix'
    TRUNCATION_RULE_NAME = 'name of truncation rule'


class TruncationLibraryButtonNameKeys(TruncationLibrary):
    # Keys used for handling the button name
    ACTUAL_NAME_OF_BUTTON = 'actual name of button'
    IS_PREFIX = 'is prefix'


class TruncationRuleElements(Value):
    pass


class CubicTruncationRuleElements(TruncationRuleElements):
    PROPORTIONS = 'm_edit_proportion_'
    SLIDERS = 'm_slider_'
    COLOR_BUTTON = 'm_color_button_'
    DROP_DOWN = 'm_choose_'
    TOGGLE_OVERLAY = 'm_toggle_apply_overlay_facies'
    CLICK_OVERLAY = 'm_button_apply_overlay_facies'


class NonCubicTruncationRuleElements(CubicTruncationRuleElements):
    ANGLES = 'm_edit_angle_'


class BayfillTruncationRuleElements(CubicTruncationRuleElements):
    SLANT_FACTOR = 'm_edit_factor_'


class TruncationRuleConstants(Key):
    TRUNCATION_RULES = 'truncation rules'
    SELECTED = 'selected truncation rule'


class CubicTruncationRuleConstants(TruncationRuleConstants):
    PROPORTION_INPUT = 'text_field'
    PROPORTION_SCALE = 'slider'
    COLOR = 'color'
    FACIES = 'chosen facies'


class NonCubicTruncationRuleConstants(CubicTruncationRuleConstants):
    ANGLES = 'angles'


class BayfillTruncationRuleConstants(CubicTruncationRuleConstants):
    SLANTED_FACTOR = 'slanted factor'


class FaciesLabels(Key):
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'


class FaciesBayfill(FaciesLabels):
    F1 = 'floodplain'
    F2 = 'subbay'
    F3 = 'WBF'
    F4 = 'BHD'
    F5 = 'lagoon'


class FaciesNameBayfill(Key):
    FLOODPLAIN = FaciesBayfill.F1
    SUBBAY = FaciesBayfill.F2
    WBF = FaciesBayfill.F3
    BHD = FaciesBayfill.F4
    LAGOON = FaciesBayfill.F5


class SlantFactorsBayfill(Key):
    SF = FaciesNameBayfill.FLOODPLAIN
    YSF = FaciesNameBayfill.SUBBAY
    SBHD = FaciesNameBayfill.BHD


class HideOptions(Value):
    DISABLE = 'disable'
    HIDE = 'hide'


class Constraints(Value):
    MINIMUM = float('-inf')
    MAXIMUM = float('inf')
    DECIMALS = -1


class Proportions(Constraints):
    MINIMUM = 0
    MAXIMUM = 1
    DECIMALS = 5


class Angles(Constraints):
    MINIMUM = -180.0
    MAXIMUM = +180.0
    DECIMALS = 2


class MainRange(Constraints):
    MINIMUM = 0.0
    MAXIMUM = float('inf')
    DECIMALS = 5


class PerpRange(Constraints):
    MINIMUM = 0.0
    MAXIMUM = float('inf')
    DECIMALS = 5


class VerticalRange(Constraints):
    MINIMUM = 0.0
    MAXIMUM = float('inf')
    DECIMALS = 5


class AzimuthAngle(Constraints):
    MINIMUM = 0.0
    MAXIMUM = 360.0
    DECIMALS = 2


class DipAngle(Constraints):
    MINIMUM = 0.0
    MAXIMUM = 90.0
    DECIMALS = 2


class Power(Constraints):
    MINIMUM = 1.0
    MAXIMUM = 2.0
    DECIMALS = 5


class Ranges(Value):
    # Slider
    SLIDER_MAXIMUM = 99
    SLIDER_MINIMUM = 0
    # Proportion
    PROPORTION_MINIMUM = 0.0
    PROPORTION_MAXIMUM = 1.0