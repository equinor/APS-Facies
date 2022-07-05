## Preamble

This document described the changes between versions of the APS GUI.

## 1.3.10

### Fixes
* Revert back to use warn as long as the library `warnings`, is used
* Create zone parameter if it does not exist when opening a grid model in the GUI

## 1.3.9

### Fixes
* Ensure that simbox thickness is calculated in the same way for both the original job and a copy created by "Save As"
* Modified error message related to Zone parameter
* Check parameter type for zone parameter in `RMSData`
* Fix bug in `modifyBlockedWellData` when zone log is `0`, or  all facies log values are undefined in a zone
* Fix the problem that the symlink from stable pointed to a non-existing plugin version

## 1.3.8

### What's new
* Add script to copy 3D parameter from geogrid to ERT box grid and extrapolate in ertbox


### Fixes
* Set default debug level to read it from model file for APS scripts running outside APSGUI
* Uses the new address/certificate for Equinor's container registry
* Updated vulnerable dependencies
* Ensure that `zone_name` is fetched from zone parameter everywhere
* Fix bug in check for facies in `createProbabilityLogs.py`
* The definition of timestamp for build-number was updated (RMS uses a signed 32-bit, and the previous number was greater than that)


### Performance
* Check if necessary to simulate GRF when using GRF with trends (that is, if the relative standard deviation is very close to `0`)
* Remove duplicated entries of probability parameters. This slows down the calculation of average of probabilities


### Miscellaneous
* Edit doc string for module to copy GRF trend from geogrid to ERTBOX grid
* Added comments in the output yml file to be included in the `global_master_config.yml` file in FMU


## 1.3.7

### Fixes
* Enable customized trends of type RMS_PARAM to be used in FMU workflows with ERT


### Miscellaneous
* Uses timestamp as build number, instead of a running number


## 1.3.6

### Fixes
* Fixing a bug that resulted in shifted localisation of the ERTBOX grid relative to the modelling grid when grid index origo was set to Eclipse standard location. XTgeo assumes that origo for rotation is the same location as the origo for the grid index
* (mock) Decode bytes to UTF8


### Miscellaneous
* Use an enum for the flip direction of grids in XTgeo
* Update dependencies
  * Linting rule changed in update


## 1.3.5

### What's new
* Respect the environment variable `RMS_PLUGINS_LIBRARY`

### Fixes

* Update dependencies with known vulnerabilities

### Miscellaneous
* Ignore vulnerable dev-dependencies in CI/CD, as these are never deployed to the user


## 1.3.4

### What's new
* Enable use of stair case reverse faults (dual indexing system)
* Default for auto-detect which fmu mode is simulated and export

### Fixes
* Better and more robust handling of rotated grid
* Use functionality internal to APS code for part of the export/import to avoid `xtgeo` limitations
* Updated dependencies to mitigate known vulnerabilities in some of them

### Performance
* Optimize Gaussian Random Field transformations in `numpy`

## 1.3.3

Includes some bug fixes for RMS 12, and 12.1, along with some optimizations.

### Fixes
* Support empty 3D grids in RMS 12
* The plugin now handle realisation numbers greater than 1
* Ensure that facies realizations is of type `numpy.uint8`
* Set QA RMS parameters to non-shared if not FMU mode and shared if FMU mode
* Remove generating empty RMS parameters for trend
* Check whether unshared grid are empty
* Fixed an error in `grid_model` for multi-realisation runs for grid
* Add check to ensure that FMU mode should always use shared grid and shared 3D RMS parameters


### Optimizations
* Vectorisation of linear, elliptic, hyperbolic, and elliptic cone trend calculation outside FMU mode
* Optimize numpy use when updating facies realization


### Restructure
* Remove unused initialisation of rms parameter.


## 1.3.2
Adds full support for RMS 12.1 (beta 2)

### Fixes
* The plugin now works with RMS 12.1 (Python 3.8)
* Importing model files in RMS 11.1 now works as expected
* Certain included workflows would cause RMS to crash, of jobs to fail, due to TK inter not being configured
  * This was caused by importing `matplotlib` in a batch job
* Ensure that the Agg backend of matplotlib is ued, when running the APS tests in headless mode (e.g. when building, and testing the plugin as part of the build pipeline)
* Do not depend on `packaging.version`, this package was included in RMS 11, but not in 12.1, which caused some issues

### Restructure
* All APS Python code moved under the `aps` namespace
  * This was already done when building the plugin, but not in the source control
* Move code for GUI outside the source folder for APS
* Move all type annotations from stubs
  * Also fixed a typo in mock's class name (roxar.grid.BlockedWell)


### Miscellaneous
* Some GUI elements are more compact
* All dependencies are updated to their latest version
* Removed unused, and unnecessary (JavaScript) dependencies
* Improved discovery of NRlib on RGS
  * Added debug output for which nrlib version is used Modify test for redhat version

## 1.3.1

### Fixes

* Fixed an issue that caused an error from TKinter
* Fixed an issue related to customized trend
* Fixed an issue that would cause future migrations to fail
* Show the representation of the error message
* Ensure that the "simple" truncation rule may be imported / loaded from a job

## 1.3.0

### What's new?
* The user may choose the transformation type
  * In both GUI, and in the model file
* A job no longer needs to be opened in order to be migrated to the newest version
  * APS jobs can now be run in batch mode, without needing to be opened first
* Modified FMU config yml format for APS parameters
  * add gui for checkbox for auto export of FMU files
* Changed print info Modified attribute and probability distribution files for FMU
* If using an APS stub in a RMS workflow, and no plugin path is given, the stable releases is used
* Option to automatically detect whether FMU is used
* Add `ROFF` format as an optional choice as exchange format for GRF field parameters between APS and ERT
* Remove FMU parameter list location
* Remove project selection

### Fixes
* Fix bug that make APS fail when running or open an existing job if Zone parameter is empty or removed
* Check azimuth angle
* Update vulnerable dependency
* Fix updating of `code_names`
* Fixed error in name of FMU tag for `RelStdDev` parameter and `RelativeSize`
* Fixed a bug when running in FMU mode with only parameter updates
* Fix leading text for some input in Job settings
* Change order of grid index origo check and ertbox grid creation
* Ensure that lower left corner is used for simbox
* Write down the name of the built plugin, and deploy it specifically
* Grid ijk-handedness is handled for both RMS standard and Eclipse standard grid index origin
* Fixed a bug in normalization. A default value was used instead of user defined value for tolerance
* Extend the script used to create probability logs so that it can handle multiple zones in general
* Add support for migrating from some legacy jobs
* Modified script `defineProbTrend`, so it works properly both when using and not using conditional probability matrix

### Restructure
* Reuse code, and make code more Pythonic

### Miscellaneous
* Give understandably error message when mismatch between old APS job and the APS plugin lead to error when running
* Consistently use helper method `get_debug_level`
* Use RMS 11.1.2, and updated test project
  * Including the provided mock data
* Add missing exports in mock
* Set the normalization parameter defaults in the run job
* Specify a new root for project files, when using a mock
* Update link to point the Equinor, instead of Statoil
* May click the "run" button locally, when developing outside of RMS
* May load jobs from GUI locally, when developing outside of RMS
* Looks for known vulnerabilities in Node.js dependencies


## 1.2.1

### Fixes
* Show export options in all FMU modes
* Do not set path to `null` when user cancels file, or directory selection


## 1.2.0

The GUI now works as expected in RMS 12.

### What's new?
* The output to FMU / ERT, is now compatible with `global_master_config.yml`
  * The GUI may write the ERT probability distribution configuration file

* The non-cubic templates where simplified
* Allow user to adjust `max_allowed_fraction_of_values_outside_tolerance`
* Overhauled how the model file, and FMU files can be exported
  * The paths are shown as relative (to the RMS project location)
  * The user may select FMU configuration paths for export
  * If some files / directories does not exist, export is disabled
  * There is a button to restore default paths
  * May not export FMU data, when no variables are updatable
* The user may change facies code of user defined facies

### Fixes
* Unit tests work as expected
* Highlight all component, when current
* Ensure `get_rms_version` gives major.minor.patch
* Ensure path is passed correctly
* Improved the documentation to make intentions more explicit

### Restructure
* Truncation rules are generated automatically fromthe specification file
* Unify selection of files, and directories
* Use dump method for exporting model file, and FMU configuration files
* Separate methods for decoding BASE64 encoded strings

### Miscellaneous
* Update dependencies
  * axios 0.19.2 -> 0.20.0
  * and others
* Remove unused images, these are generated automatically
* Improved the documentation for how to start the GUI locally
* Defined a DAG in CI/CD


## 1.1.5


### Fixes

* Makes `ERTBOX` the same _physical_ size as the simulation box

* Ensure `ERTBOX` has the same handedness as simulation grid

* Facies may now have a code of `0`

* Ensure current zone exists before selecting it as current

* Ensure a discrete item's code is an integer

* Ensure that the "Zone" parameter exist

* Fixed a bug that caused parameters to not be shown

* Non-required keywords may be empty

* Update version, when migrating older versions of the state

* Skip non-defined zonations

### Restructure

* The component `HighlightCurrentItem.vue` is no longer needed



## 1.1.4

### What's new?
* Added more detailed warning in `createProbabilityLogs`

### Fixes
* Add necessary type annotations
* Remove vuetify's explicit type decelerations
  * This caused the entire build to fail, as there where two type errors in Vuetify


### Miscellaneous
* More detailed warning for when facies where not observed
* Updated dependencies, to patch a security vulnerability
  * Along with other dependencies
* (**TEMPORARY**) Allow safety check to fail
  * The reason for this, is that the docker image has a very old version of sphinx installed (1.4), but the fix for the vulnerability is for 3.0.4.


## 1.1.3

### Fixes

* Ensure that checking vulnerable Python packages can be done again
  * Done by updating `pipenv` to a newer (pre-release) version


### Miscellaneous
* The packets sent between RMS, and the license server is logged
  * Necessary to open which ports for the build server
* Update Node.js, and Yarn to latest stable (12.16.3/1.22.4)


## 1.1.2

A minor bug fix release, which addresses some issues discovered on the Peregrino project.

### Fixes

* The calculation of the simbox thickness is now more robust agains zones with inactive cells in their top, and bottom layer

  * If the thickness cannot be calculated, a default of 30 is used

### Restructure
* Reused som common code
* Improved formatting of code base


### Miscellaneous
* Updated dependencies; there was a [security vulnerability](https://github.com/pyupio/safety-db/blob/9cb84541a691044512dab8422dc2a36383e0fff3/data/insecure_full.json#L10825) in [pylint](https://www.pylint.org)
* chore: Update dependencies


## 1.1.1

A minor bug fix release

### Fixes
* Include new package in XTgeo's dependencies ([packaging](https://pypi.org/project/packaging/))

## 1.1.0

This release includes many bug fixes, and quality of life improvements.

### What's new?
* The 'has dual index system' property is now available in the client
* Popover / tooltip for dropdown menu
  * Allow simple(?) HTML in tooltip
* Facies observed in wells are automatically selected when choosing a zone /region
  * This behaviour may be turned off in job settings
* The user may now select values for the ERTBOX thickness that are less than the largest zone
  * The reason for this, is to be able to write in values in a sensible maner (e.g. without _having_ to use the arrow keys)
  * In order to prevent invalid values in the simulation, the user is not allowed to save the job settings if the thickness is too small
* All three main components of the GUI may now be _individually_ scrolled.
* The grid's handedness is adjusted to work well with nrlib, whenever necessary, and then reversed after the simulation is done
  * Except when the grid has reverse / staircase faults
* The user may clear the selected facies in a Bayfill truncation rule
* The requirement that each facies in a Bayfill truncation rule must be _unique_ was enforced in the GUI
* The selected paths in Job Settings, are shown in their entirety
  * If the path is too big to fit on a single line, the field expands
  * If the path does not exist on disk (due to misspelling, moving the project to a different RGS node, or other) a warning / error is shown
  * _**Note**: The reason for expanding the field, rather than shown the end of the field is that the latter turned out to be rather difficult, and non-trivial._


### Fixes
* Ensure blocked well (log) is not an empty string
  * This caused the API to look for blocked well (log)s that did not exist, and failed
* Grids with reverse faults / staircase faults works (with some exceptions:)
  * ERT mode is disabled, and a tooltip notifies the user beforehand.
  * The grid is NOT rotated to align with NRlib's coordinate system
  * The user sees a warning in a popover, informing them of incompatibility with ERT
* More accurate type annotation
* hotfix: Updated vulnerable package (pyyaml 2.3.0 -> 2.3.1) to mitigate security vulnerability
* Uses RMS' site packages in addition to "hard coded" RGS specific path(s)
  * This resolves an issue, running the plugin on RHEL 7
* Attempt to remove module, ignoring its possible non-existence
* Support enforcing minimum version of a package
  * In particular, `xtgeo` _must_ be of version 2.5.0, or higher
* The normalisation of probability cubes used in regions now works as expected
  * Updated documentation / descriptions in accordance with suggestions from Oddvar Lia
* Some type annotations where incorrect, and thus lead to possible errors
* Since there are issues with using regions in the context of ERT / AHM, these two options are now mutually exclusive.
  * The user is presented with a warning, when selecting regions, and messages are shown explaining why elements are disabled.
* Fixed index error in Bayfill truncation rule algorithm


### Restructure
* Removed extraneous code
* Changed the import order in `ChooseGridModel.vue` to be more consistent
* Made code [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)-er
* `get_grid_model_names` -> `get_grid_models`
  * Made name consistent with the method's behaviour
  * The previous `get_grid_models` was removed, and type annotations where improved
* The warning in `FmuSettings.vue` are now a self-contained function
* f-string is used in the import module
* Previously, there where two definitions of `Parent`, one containing the full objects, while the other contains the IDs. The latter was renamed to `ParentReference`
* Entities dependent on zone / region, now uses the respective instances instead of ID references
  * The `populate` actions where updated accordingly (i.e. to fetch the instances from the references)
* More accurate type annotations
* Removed (almost) duplicate implementation of the `identify` function
* Moved some definitions to avoid circular imports
* Makes the code base a little more [PEP-8](https://www.python.org/dev/peps/pep-0008/) compliant.
* Made the component for polygon table for Bayfill truncation rules easier to understand
* The path selection in Job Settings was reused as a separate component
  * The text area was expanded, and the button for selecting a directory was replaced with an icon

### Miscellaneous
* Corrected spelling of `deselect`
* Avoid API calls when blocked well (log) is set to be empty


## 1.0.0
Now that TDG4 is approved, the APS GUI is ready for general usage.

There are no mayor new features in this release, compared to 0.13.0, but rather much polish, and quality of life improvements.

The biggest change, is that jobs save with version 1.0.0 of the GUI will be able to be loaded in newer versions of the GUI.
**NOTE**: If there is a problem, please contact us, and **DO NOT** save the job, nor the RMS project, as this is likely to corrupt the job.

If you are using the APS scripts in a RMS workflow, these should be updated, as they have been slight tweaked.

### What's new
* Do not require BW in order to add Facies. Closes #251
* Checks that zones have conformity set, when required before executing the APS workflow
* More warnings are presented, when the change will _irreversibly_ (when saving) remove model parameters
  * Warns user if they add Facies, then chooses a blocked well

* Warn the user when they use custom trends in ERT-mode, as this is not yet supported
* A warning is given the user if they select a new grid model
* A new ERT grid ("ERTBOX") is created, if none is given
* Added support for running jobs in FMU / ERT / AHM
  * Parameters are adjusted to fit inside the ERT-simulation box
    * Trend location
    * Simulation box thickness
    * and more
* May read `global_variables.yml`
* The user may refresh the data in the GUI, if the data from RMS is changed
* May change facies code iff no blocked well log is given
* Allow the user to override the factor of "unsuitable" cells in probability cubes
* The selection criteria for the ERT grid has been restricted
  * While the default size was made as small as possible

### Deprecations
* Remove unnecessary dependencies, and code
  * Removed all references, and usage of `libdraw2D`
* RMS10 is no longer supported, and the individual jobs / stubs, are likely to fail due to the usage of Python 3.6 syntax (RMS 10 uses Python 3.4, which was [End of Life as of Math 18th, 2019](https://www.python.org/downloads/release/python-3410/))

### Fixes
* Consistent usage of `model_file` in workflow jobs
* Ensure deterministic dependencies, and builds
* Only set uncertainty mode (i.e. not ERT-mode) when importing a model file with FMU
* Uses the location of global variables-folder specified by user (only when in FMU-update mode; not in ERT-mode)
* Changing order of overlay facies is now always possible
* The Gaussian Random Fields, and Facies realisations in the previewer now has the same orientation as in RMS
* Ensure that the zone parameter exists
* The `MAKE` environment varariable was used by node-pyg, causing compilation error
* `roxar`, and `project` **MUST** be imported in `main.py`, and then passed along
* Some logical errors where resolved
* Only one FMU setting may be selected at the time
* Remove directory tree, instead of just attempt to remove folder
* Do not fetch data while a job loads
* Do not save the RMS project when running a job

### Restructure
* Improvements to the code base
  * More [PEP](https://www.python.org/dev/peps/pep-0008/) compliant
  * Greatly improved type annotations
  * Removed old, unused code
  * Made the code base [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)er
  * Separated logic for reading, and parsing the global variables files
  * Consistent usage of global variables
  * Moved the mock to be (somewhat) self contained
    * This, in preperation for the mock to become a separate PyPi package
  * Improved code style, to be more consistent, and compliant with ESLint
* feat: Ensure all arguments to `run` are given as keyword arguments
* Project settings was renamed to Job settings, as these settings may vary between jobs
* Specify that the preview GRFs are transformed
* Collect debug files in a zip file
* Raise an exception in stead of warning when fields are missing in the import
  * Accept missing fields that are NOT used in the zone's truncation rule


### Miscellaneous
* The dependencies where updated
* The step for making documentation, in the CI/CD was removed


## 0.13.0
The main new feature of this release, is the integration with FMU / AHM / ERT.

There are also several bug-fixes, and improvements.  Most of them, are related to making the APS GUI production-ready, and to iron out some usability issues.

### What's new
* Support for running APS in ERT / AHM / FMU
  * Import / export of fields used in FMU from / to disk
  * The user may specify each zone's conformity
    * This information is captured in the model file with the new keyword, GridLayout
  * The user may, still, update from FMU variables, without simulating GRF in FMU simbox
  * If the model file has any parameters that are FMU updatable, the GUI will assume the imported model is to be run as a FMU / ERT job
  * The user may select whether to import, or simulate fields
  * Added support for reading seed from the file ERT uses (`RMS_SEED_USED`)
  * Updates model file relative to FMU thickness
  * Hide FMU checkboxes when not in FMU mode

* Initial support for ensuring backwards, and possibly forwards, compatibility

* Allow user to set debug level
  * Write model file, and state to disk if debugging "run"

* These release notes may be viewed in the GUI
* Truncation rule templates are now presented as images

### Deprecations
* Do not allow simulation of `RMS_PARAM`


### Fixes
* Get, and use the correct zone thickness for all zones
* Ensure state is clean when loading new job
* Miscellaneous fixes to the export, and usage of the RMS mock
* More explicit error message if the given input is not a string
* Moved compare outside of unit tests, as it is used elsewhere
* Create fields if they do not already exist
* Updated default name of 'global IPL file'
* Use unicode when writing model file
* Ensure that the relative size of an ellipse is given in %
* Overlay Facies is no longer toggled when selecting a template
* Updates workflows when changing `master` and `develop`


### Restructure
* Moved trend calculation to the simulation step
* Changed the default colors for Facies and Gaussian Fields
* Improved various descriptions clearer, and less confusing
* Created cached class of grid attributes
* Removed old, and unused code
* Reuses similar logic, and control flow
* Improved type annotation
* Consistent usage of `global_variables` instead of `global_include`
* Cleaner API, and more compliant with PEP8
* Renamed the "Default" colors to "APS"
* Gathered all usage of 'NONE', and 'RMS_PARAM', when checking type
* 'Curvature of ellipse' -> 'Curvature'


### Miscellaneous
* Ignores test data
* Updated dependencies


## 0.12.0
This release _mostly_ fixes various issues.
Some of the feedback from the First User has been addressed.

### What's new
* The plugin is now self-contained
  * the user no longer need to set additional paths in RMS from APS, and NRlib
  * Workflows in RMS runs from the plugin
* The settings from a Zone/Region may be reused in a different Zone/Region
* Components that may not be used, are disabled
  * When hovering over something disabled, an explanation will often be presented
* Introduces user selectable color pallets for Facies and Gaussian Random Fields
* If the user changes the well log parameters, a warning is resented
* When Gaussian Random Fields changes, their simulation becomes grayed out
* All `alert`s where replaced with a banner message

### Fixes
* Fixed various regression errors
* The user options will now be restored, when opening a stored Job
* Selecting a Zone/Region no longer causes it to be the current Zone/Region
* Region parameters with no names are allowed
* The facies realization parameter now updates continuously
  * There is no longer a need to deselect the area, or click `enter`
* The workflows should now work on RMS 10
* Probability cubes must no longer start with `prob`
* Workflows now work in RMS11.1 RC / 12
* Multiple usability issues

### Restructure
* Improved code quality
  * Removed unused methods, and components
    * Support for sliders was removed
  * All components have been migrated to TypeScript
  * The internal state is now more consistent
* Comparing floats to unity is now more robust

### Miscellaneous
* Dependencies where upgraded
  * Vuetify 2.0, with its new grid

## 0.11.2

### What's new
* Added script to initialize an RMS project for APS
  * Available at `/project/res/APSGUI/initialize-project.sh`
  * Added option to save generated workflows in a temporary directory, which is used by this script

### Fixes
* The job `APS_simulate_gauss_singleprocessing.py` will now respect the `<WriteSeed>` keyword in model files
* Facies probabilities will no longer be reset when changing truncation rule template
* The region parameter should not be selected, and hidden if only one option exists
* Facies may now have a probability of `0`
* The path to the project used the wrong action to store the value
* Only update branches in `/project/res/APSGUI`
* The detection of with version of RedHat is used on RGS has been made future-proof

### Restructure
* All references to `writeSeeds` have been renamed to `write_seeds` (PEP8)
* Minor improvements to the type annotations

### Miscellaneous
* Minor improvements to the code base

## 0.11.1

A minor release that fixes a couple of issues related to import/export of trends

### What's new?
* Commits to `develop` are released to `/project/res/APSGUI/releases`, as an unstable release
  * If a commit is tagged, it will be released as a stable version to `/project/res/APSGUI/releases/stable`


### Fixes
* During import, the `type` of trend, was not handled
* During export, `relativeSize` was, mistakenly, given as `curvature` in the model file

## 0.11.0

This release contains _a lot_ of bug fixes.


### What's new?
* Facies Autofill is disabled for production
* When the CI/CD-pipeline for `develop` succeeds, a new plugin is added to develop
* If the user selects more facies than the truncation rule can hold, the GUI will assume that the user will be using overlay
* the user may no longer edit, or delete facies from RMS
* Introduced the concept of some Facies being from RMS, while others are user defined
* Sets the maximum size of cubic specification to 400 pixels
* Added support for maximum size of plots
* If the user chooses to use overlay facies, the necessary Gaussian Fields will be created, if there are too few


### Fixes
* The built plugin file is stored
* The mock, and Docker image has been updated to use the latest test project
* Temporary ROFF-files are removed before integration tests
* Ensures that necessary files are created during the integration tests
* More accurate behaviour regarding assigning code_names
* Id the given directory for `seedLogFile.dat` does not exist, it is created
* The random seed of Gaussian Random Fields is loaded from model files
* The arrows for changing the order of polygons, now works as expected
* The FMU parameters for non-cubic trends are now consistent with the documentation
* Cubic truncation rules were imported incorrectly
* Probability cube names are no longer ignored while importing a model file
* Improvements to the mock
    * Properties may be written to the mocked project instance
        * they will be remembered as long as the `Project` instance lives
    * Improved how collections are presented in PyCharm's inspector
    * Unset properties should not need arguments, or fail when arguments are given
    * Increased performance of `get_cell_numbers_in_range`
    * Ensure that boolean values are returned from `shared` in `Propery`
* The names for discrete parameters should now be written to the grid / property
* Root getter return instance of `GlobalFacies`, not just the `ID`
* `hideAlias` was not passed as a property to the `FaciesSelection` component
* Logical errors has been corrected
* Only the facies that are _SELECTED_ should be counted, when deciding if a truncation rule has enough facies
* The user may now change which Gaussian random field is associated with which &#593;-direction
* Which Gaussian fields are available for the different facies, and &#593;-direction has been fixed, as to be consistent with the rules of APS
* Uses dedicated action for changing color; colors may not be changed
* The correct &#593;-channel is now displayed for a given Gaussian Random Field
* Gaussian Random Fields should have the same zone / regions as the truncation rule
* Ensure that there is only ONE specification for all fields for a zone/region
    * Gaussian Fields of vertical cross section is now possible again
* Uses recommended search of XML elements
* Increased the timeout for calls from the GUI to RMS
* A cubic truncation rule may not be split into less than two polygons
* Jobs should not be reloaded after clicking run in RMS
* Ensure facies names are not renamed while importing, and exporting a model file, or loaded from a saved job
* A number should not be considered as empty
* Consistent alignment of truncation rule specification
* More descriptive truncation rule titles
* Gaussian Random Fields are not loaded correctly from saved jobs
* Added circular import check to CI
* Check that all facies are used, before updating the truncation map
* Check that truncation map can be updated before reacting to changes in selected facies
* Polygons with no facies should not have their fraction editable
* Do not show fractions if no polygon has a facies
* Enforce normalization of (facies) fractions
* Do not write `seedLogFile.dat` when running the simulation from RMS
* Uses default name, and pass realization number as keyword
* Ensure that probabilities are normalized
* FMU values are returned only if the field is supposed to be updatable


### Restructure
* The RMS job `rms_jobs/Create_bw_prob_log_from_deterministic_facies_log.py` is not used, and has been removed
* Uses extended XML representation, when importing a model file
* Added more type annotations
* Introduced an `add` action for cross sections
* Extracted the creation of Variogram/Trend and uses existing method for parent
* Static plots now listen for resize
* Introduced the interfaces `Ordered`, and `DiscreteConfiguration`
* The `PreviewHeader` component now takes a truncation rule as property
* Moved definitions to avoid circular import dependencies
* The configuration has been made dynamic
* Moved common functionality for fraction specification
* Improved the code quality

### Miscellaneous
* Removed extraneous whitespaces, and converted tabs to 4 spaces
* Added more logging
* The dependencies has been updated
* The cubic specification has been made larger


## 0.10.1

A Minor fix for an import that caused the GUI to not load from RMS

### Fixes

* Imports `roxar.rms` for the API

## 0.10.0

This release includes two major features; cubic truncation rules, and the implementation of the `run` button in RMS.
When click, the APS simulation, and truncation workflows are executed, and the result is written back to RMS.

RMS 11.1 add support for staring plugins from the context menu when different data is selected.
As such, if the APS GUI is started when a specific grid model is selected, that model is preselected in the GUI.

Additionally, there are _many_ improvements, fixes, and some performance gains.
Multiple regression errors in 0.9.1 has also been addressed.

### What's new?
* Implemented Cubic truncation rules
* The user may click 'run' in RMS, and the APS simulation will be executed
* The project / file name field has been removed from toolbar
* Aliases of Facies are used, instead of their names
* Select the given grid model from RMS (requires RMS 11.1, or newer)
* Loading indication of Zones, Regions, and Facies
* Sets default Facies Realisation Parameter to 'aps'
* Gets parameters from RMS
  * Current workflow name
  * Project name
* Added version information, in the GUI, and in the plugin file
* The seed of a Gaussian Random Field will now be exported
* Help icon with hover text

### Fixes
* Added missing \_\_init\_\_.py in the root of the plugin
* Preserve the `FmuUpdatableValue` class in Gaussian Random Fields
  * Set curvature to be FMU updatable when changing to hyperbolic trend
    * Which caused the `curvature` field in a model to be empty if the user selects `HYPERBOLIC` trends
* Ensures that project name is the name of the project on disk
* Adds region parameter to model file __only if__ regions are used
* Ensure types of truncation rules are in the same order
* Mock
  * Uses the correct container for data
  * Implemented `set_shared`
  * Data is extracted
  * Data is gotten from the correct realisation
* Defer build number until it is needed
* Truncation rule types are added once

### Restructure
* Improved readability, cleaned up the code base, and made it more robust
* Added more, and improved type annotations
* Moved export logic to separate file for easier reuse
* Moved `APS_main.py` to `rms_jobs`, as it is used as an RMS job
* Allow `seed_file_log` to be set
* Regions now ONLY exist inside zones
* Uses consistent API for (nested) 'selectable'
* Made `matplotlibrc` into an "heredoc"
* `selected` is handled by classes, instead of directly by state

### Miscellaneous
* Updated dependencies
* Added target for listing all available mock projects

### Performance
* More efficient serialization of domain objects
  * Smaller size of RMS jobs (reduced size by a factor of around 6)


## 0.9.1

### Fixes
* Fixed a regression error that caused the facies realizations to not render

## 0.9.0

The majority of changes here, is related to the migration from JavaScript to TypeScript.
The domain model has been rewritten entirely in TypeScript, while many Vue components has been migrated to TypeScript.
There has also been a number of user interface / experience improvements.

### Features
* Import of model files is enabled for Bayfill and non-cubic truncation rules
* Added labels of facies alias to the truncation map
  * Automatic contrast adjustment
* Show color scale of Gaussian Random Fields

* The currently selected element is highlighting
  * Zone / Region
  * Facies

* Added button for the Equinor wiki page on APS
  * Added a helper text on the help icon when hovering

* The blocked well parameters are _always_ shown, even when they can only have one possible value
  * blocked well log parameter
  * blocked well parameter
* Added a spinner when loading a model file, or a previous job from RMS
* Added option to toggle facies filling

### Fixes
* FMU Checkboxes are checked when the value is updatable
  * This caused then not to be selected, when a model file was loaded
* Ensure the 'Roboto' font is rendered in plots
* Fixed a bug in bayfill rule which appeared in polygon calculations when BHD probability was 0
* Ensure that if Zone parameter does not exit in the RMS grid_model, it will be created when needed in `APS_normalize_prob_cubes.py` and in `APS_main.py`
* For the test project, blocked wells log has been renamed
* Ensure that dicts in templates are not reused when initially same
* Ensure that the state is emptied before importing model file
* Ensure properties from RMS are non-empty in current realisation

### Restructure
* Introduced TypeScript
  * Migrated domain to TypeScript
  * Migrated components to TypeScript
* Restructured import for new state (Bayfill)
* Moved 3D cut to be depend on zone/region instead of on GRF
* Moved alpha specification above truncation rule specification
* Size change is moved to watched property; more robust
* Return Promises.all, instead of simply dispatching actions
* Made operand be first on newline; more readable
* Replaced `Promises` with `async`/`await`
* Translated error messages to English

### Miscellaneous
* Removed `vue-router`, as it is not used in a meaningful way
* Updated dependencies
* Added target for detection of circular imports
* Added the integration test `Test_defineFaciesProbTrend`
* Added the Karoo Fan3 dataset, as mock data
* Increased font sizes
* Minor code cleanup
* Code coverage in tests
* Added a small explanation that Cubic truncation rules are not shown

### Performance
* Loads an initial rougher estimate of simbox thickness, and then loading more accurate estimates in the background


## 0.8.0

This release mostly targets fixes, and polishes so that the GUI is usable to end users.
That is, there where some breaking bugs that are now fixed.

These bugs concerns opening the GUI, Overlay Facies, Background Facies, and Export of the model file.


### Features
* Exporting a model works as expected
  * When exporting, the user is presented with a dialog to choose where to model is stored
* When a previous job is loaded from RMS, a spinner is displayed for the duration of the loading time
* When calculating the average of probability cubes, the `AVERAGE` button is disabled, and spinning
* The default sizes of plots are increased

### Restructure
* The default values for trends are updated to be more usable
* `matplotlibrc` is automatically generated, with a different backend depending an platform and usage
* The `<MainFaciesTable>` tag in the model file has gotten two new attributes
  * `blockedWellSet`
  * `blockedWellLog`
* Introduced `BackgroundGroup` to better enforce overlay constraints

### Fixes
* Facies are now _always_[^1] presented in the same order (by `code`)
* Calculating probability cubes now work correctly when regions are selected
* A probability cube may be used in multiple zones / regions
  * but not twice in the same zone / region
* Resolved an issue that caused to GUI to not open properly
* Fixed numerous issues regarding Overlay
* When selecting `RMS_PARAMETER` as a trend, the export failed
* Bayfill polygons where in the wrong order
* When fetching `blockedWells` and `blockedWellsLog`, the current parameter is unset
* Fixed some _minor_ user interface glitches
* Truncation rule types where fetched multiple times in stead of once
* When an RMS job was loaded, some of the information was not restored
* Plots in the GUI are now consistent with plots from `testPreviewer`
* Curvature _must_ be greater than `1` for `HYPERBOLIC` trends
* The order of Gaussian Random Fields has been made consistent
* The probabilities in the exported model file is now consistent with what is shown in the GUI


### Miscellaneous
* _Minor_ code improvements
  * Duplicate, or similar code are now written once
* Dependencies have been updated
* Updated proxy / firewall settings


## 0.7.0

The GUI should now be ready for first use.

The big change for this release, is the way overlay facies are specified in the GUI.
The user may now specify a complete non-cubic truncation rule with an arbitrary number of (overlay) polygons.

### Features
* The included templates for truncation rules have been updated
  * New naming convention for generic rules
  * Added concrete examples for Mariner
    * Implemented some Cubic rules as Non-Cubic
  * The templates are sorted by number of necessary Facies (and secondarily in alphabetical order)
* Added save dialog to let user define where to export file to

### Restructure
* The need for `seed.dat` has been removed from APS modeling (single processing)
* `matplotlibrc` should now be read appropriately
  * **Note**: This may cause the test previewer to fail on some systems
* The mock now uses HDF5 instead of a `tar.gz` archive
  * Various edge cases, and issues with the mock has been resolved
* The custom buttons are now easier to use
* The way facies are gotten in the GUI has been simplified
* Changed the way overlay facies is specified
  * This allows some of the more complex constraints on specifying truncation rules to easily enforced, and to lift some of the mental burden from the user
* Introduced a global config file for constants in the GUI
  * The default size of plots
  * The default color scheme
* Added the attributes `blockedWell`, and `blockedWellLog` to element MainFaciesTable in the model file


### Fixes
* Will now handle cases where number of specified gauss fields in a zone is larger than number of gauss fields used in truncation rule for the zone.
* Ensure that the user can specify more than one polygon per background facies group
* Validation of exported APS model is done **only** when the creation of the file is successful
  * A single error message is presented to the user
* If user selects an invalid path and saving fails, the user is alerted (in the GUI)
* The existence of empty overlay, or overlay being disabled no longer causes the export to fail

### Miscellaneous
* Some more cleaning of code
* Unused code has been removed
* Added various Quality of Life improvements to the codebase
* Dependencies are kept up to date
* Allows the grid azimuth to be negative

## 0.6.0

### Fixes
* The RMS license server has been changed
  * Upgraded RMS (11.0.0 -> 11.0.1)

## 0.5.0
The user may now see how the gaussian fields, and truncation rule will look in the previewer.

### Features
* Visualises the realisation of a given Truncation Rule, and Gaussian Random Fields
* Visualises all Gaussian Random Fields that are specified for a given zone/region
* Cross plots of all combinations Gaussian Random Fields
   * That is given to it
   * As of now, the number of Gaussian Random Fields shown in the previewer _may not_ be limited
* The default values for a Gaussian Random Field have been updated:
    * Default simulation box size: (100, 100, 1) -> (1000, 1000, 10)
    * Default `power`: `null`/0 -> 1.5
* Gaussian Random Fields are now simulated when they are created; no need to click `refresh` on default values in order to see their result

### Restructure
* A Truncation Rule/Gaussian Random Field holds its latest realisation
   * **NOTE**: Currently, there are no built in checks to see whether the (realisation) data is synchronised with the specification
       * May use a hash of the serialisation of the rule as a check
* Two new buttons for updating fields
    * Two dice => use a new random seed
    * Arrows / refresh => Calculate the field again, using the same seed
        * **NOTE**: To make it spin, while the data is being fetch, FontAwesome had to be used for icons in stead of Material Design Icons (which we used)
* Using the icons from FontAwesome instead of Material Design Icons
    * Option to upgrade to a pro plan, for more, and nicer(?) icons
* The check for whether a truncation rule may be calculated or not, has been moved to a `state` getter / method, instead of a computed property
* `BoldButton` now inherits from `WaitingButton`
* Made repeating code/logic/markup of a "waiting button" into a separate component
* More air/space between elements when specifying a Gaussian Random Field

### Fixes
* Removed an old 'hack', as a propper fix has been found
* lodash is now its own item in `babel.conf.js`
* Upgraded Python dependencies, as there has been discovered a security vulnerability in `requests`
* Made the way a component fills its parent more consistent
* Errors from the API should be propagated to the GUI

### Technical debt
* Made a function for flattening 2D arrays
    * The version of Chrome (56) in RMS is too old for the required function (`Array.prototype.flat`)
* Shows _all_ defined Gaussian Random Fields, and their cross plots
    * Simple to implement a (user defined) restriction

## 0.4.3

### Restructure
* The zone parameter (usually `Zone`), is no longer needed, as we bay get them directly from the grid model, through `zonation`.

### Fixes
* Removed files that should not have been included

## 0.4.2

### Restructure
* Restructured truncation rules (some from !144), so that they always has the property `type`, and thus we avoid another error.

### Fixes

* An issue where the user was unable to add a new Gaussian Field as been resolved.
* The order facies / polygons are given in the template, is preserved.


## 0.4.1

### Fixes
* Fixed an issue that caused the facies table to disappear


## 0.4.0

### Features
* Added support for saving, and loading jobs in RMS
* Lets the user give an alias to a facies
* The GUI may import an XML model file
* Lets the user specify the Bayfill truncation rule
  * When selecting a facies that has already been selected in the truncation rule, the facies swap
* Added integration tests with RMS (workflows)
  * Temporarily disable workflows that don't behave;
* Lets the user specify the probability (cubes) for a given facies
* Gaussian Random Fields are dependent on / know their zone and region
* The user may choose to list zones and regions with their code, or name

### Fixes
* Added empty/trivial cases for cubic and non-cubic truncation rule
* Cypress has been removed

### Restructure
* Made updating facies more robust
* Uses new vuetify-loader and Vuetify 1.3
* Wrapped 'button icons' into separate component
* All imports (JavaScript) uses `@/` for local components

### Miscellaneous
* Zones and Regions are expandable
* The entire GRF panel is expandable
* The codebase has been cleaned


## 0.3.2

### Features
* New design, and behaviour of the facies table
* Includes a mock of the RMS test project for easier debugging, and introspection
* Toolbar for managing model files

### Restructure
* ag-grid has been replaced by Vuetify's own tables

### Miscellaneous
* Various bug fixes, and code quality improvements


## 0.3.1

### Features
* Added a mock of RMS 11, and the data from the test project `testApsWorkflow_new.rms11`
* Facies are given default colours, and the user may easily change them at will.
* Added files
    * `APS_set_seed_file_for_multiprocessing_workflow.py`
    * `SetStartSeedForRealization.ipl`
    * `APS_normalize_prob_cubes.py` (RMS job)
    * `createProbabilityLogs.py`
    * IPL scripts used in test workflow
* Added buttons, and dialogs to the tool bar
    * Limited functionality;
        * Upload model files
        * Validate model files
        * Set project settings

### Fixes
* Fixed a bug that caused the workflows to fail when the region parameter was not given, or was given as `None`
* Each zone has their own list of regions, _independent_ of each other
* The GUI remembers which zones and regions are selected, when changing the zone

### Restructure
* Cleaned up various formatting
* The keywords RMSProjectName and RMSWorkflowName should be optional not required
    * Also Preview should be optional as decided in status meeting Wednesday August 15th
* Make the design of the Facies table match the design of the Zone, and Region tables.
* The current facies (for deletion) is highlighted
* Renamed example files due to renamed grid models in example project
* Updated unit test reference data for Trunc2D_Angle since tolerance values in algorithm are adjusted

### Miscellaneous
* Bumped version number to 0.3.1, as this will be intended to be used, and tested
* Migrated **back** to Vuetify's [data-table](https://next.vuetifyjs.com/en/components/data-tables), instead of [ag-grid](https://www.ag-grid.com)
    * The former was easier to work with, when interacting with the table, and data (e.g. highlighting current, showing which regions/zones are selected, and their relationship)
* The _current_ zone/region is highlighted (in **bold**)
* Regions (in the store) are mirrored from the current zone's regions (Vuex plugin)
* May show/hide name, and code columns at will
  * Default, is to show them for the region, and zone table
  * This will be user configurable in the future
* Updated the dependencies

## 0.3.0

## 0.2.0

## 0.1.6

## 0.1.5

## 0.1.4

## 0.1.3

## 0.1.2

## 0.1.1

## 0.1.0

---

[^1]: Except when toggling the order in the Global Facies Table

