## Preamble

This document described the changes between versions of the APS GUI.

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


