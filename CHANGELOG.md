## Preamble

This document described the changes between versions of the APS GUI.

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

