#!/bin/env python
# -*- coding: utf-8 -*-
import os.path
import copy

from pathlib import Path
from aps.utils.ymlUtils import readYml
from aps.utils.constants.simple import Debug

class APSConfig:
    """
    Initialize with standard FMU directory structure and
    default settings for APS.
    The init function can be used to create a config file.
    """
    project = None
    debug_level = Debug.OFF
    config_file_without_path = "aps_config.yml"
    config_file = None
    use_config_from_file = False
    create_config_file = False
    rms_project_directory_path = None
    config_initial = {
        "top_directory_relative_to_rms_project": "../..",
        "relative_paths":  {

            "fmuconfig":         "fmuconfig",
            "fmu_config_input":  "fmuconfig/input",
            "fmu_config_output": "fmuconfig/output",
            "global_variables_file":  "fmuconfig/output/global_variables.yml",

            "ert":               "ert",
            "ert_model":         "ert/model",
            "ert_dist":          "ert/input/distributions",

            "rms":               "rms",
            "rms_model":         "rms/model",
            "rms_field":         "rms/output/aps",
            "aps_model_export":  "rms/input/config/aps",
        },
        "aps_file_extensions":  {
            "fmu_master_config": "_aps_params.yml",
            "fmu_config":        "_aps_fmu_params.yml",
            "ert_fields":        "_aps_fields.txt",
            "ert_prob":          "_aps_dist.txt",
        },
    }
    config = copy.deepcopy(config_initial)


    @classmethod
    def init(cls,
            project,
            use_available_config_file: bool = False,
            must_read_existing_config_file: bool = False,
            check_existence_of_paths: bool = False,
            debug_level: Debug = Debug.OFF,
        ):
        """
        use_available_config_file: Turn on/off whether to read FMU directory config from file or not.
                                   If turned on and config files does not exist, it will be created.
        must_read_existing_config_file: If turned on, config file is re-read even if it has already been read.
        """
        cls.debug_level = debug_level
        cls.project = project
        cls.rms_project_directory_path = str(Path(cls.project.filename).parent.absolute())
        cls.config_file = cls.rms_project_directory_path + "/" + cls.config_file_without_path
        # Create and use config file
        if use_available_config_file:
            if not os.path.exists(cls.config_file):
                # Write new config file using standard config settings
                cls.config = cls._create_aps_config_file()
            else:
                if not cls.use_config_from_file or must_read_existing_config_file:
                    cls.config = cls._read_aps_config()
            cls.use_config_from_file = True
        else:
            # Use default setting
            cls.config = copy.deepcopy(cls.config_initial)
            cls.use_config_from_file = False
        if check_existence_of_paths and use_available_config_file:
            cls.check_file_and_directory_existence()

    @classmethod
    def project_dir(cls):
        if cls.project is None:
            raise ValueError("Internal error: Must initialize APSConfig with init function")
        return cls.rms_project_directory_path

    @classmethod
    def get_config_file(cls):
        return cls.config_file

    @classmethod
    def use_fmu_config_file(cls):
        return cls.use_config_from_file

    @classmethod
    def global_variables_file(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["global_variables_file"]

    @classmethod
    def global_variables_file_absolute(cls):
        return cls.project_dir() + "/" + cls.global_variables_file(cls)

    @classmethod
    def top_dir(cls):
        return cls.config["top_directory_relative_to_rms_project"]

    @classmethod
    def top_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.top_dir()

    @classmethod
    def rms_model_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["rms_model"]


    @classmethod
    def rms_model_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.rms_model_dir()

    @classmethod
    def aps_model_export_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["aps_model_export"]

    @classmethod
    def aps_model_export_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.aps_model_export_dir()

    @classmethod
    def fmu_config_input_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["fmu_config_input"]

    @classmethod
    def fmu_config_input_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.fmu_config_input_dir()

    @classmethod
    def fmu_config_output_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["fmu_config_output"]

    @classmethod
    def fmu_config_output_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.fmu_config_output_dir()

    @classmethod
    def ert_model_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["ert_model"]

    @classmethod
    def ert_model_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.ert_model_dir()

    @classmethod
    def ert_distribution_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["ert_dist"]

    @classmethod
    def ert_distribution_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.ert_distribution_dir()

    @classmethod
    def rms_field_dir(cls):
        return cls.top_dir() + "/" + cls.config["relative_paths"]["rms_field"]

    @classmethod
    def rms_field_dir_absolute(cls):
        return cls.project_dir() + "/" + cls.rms_field_dir()

    @classmethod
    def rms_field_dir_for_run_path(cls):
        return cls.config["relative_paths"]["rms_field"]

    @classmethod
    def fmu_master_config_extension(cls):
        return cls.config["aps_file_extensions"]["fmu_master_config"]

    @classmethod
    def fmu_config_extension(cls):
        return cls.config["aps_file_extensions"]["fmu_config"]

    @classmethod
    def ert_config_fields_extension(cls):
        return cls.config["aps_file_extensions"]["ert_fields"]

    @classmethod
    def ert_config_probs_extension(cls):
        return cls.config["aps_file_extensions"]["ert_prob"]

    @classmethod
    def get_config(cls):
        return cls.config

    @classmethod
    def get_debug_level(cls):
        return cls.debug_level

    @classmethod
    def check_file_and_directory_existence(cls):
        file_paths = [
            cls.global_variables_file(),
            cls.fmu_config_input_dir(),
            cls.fmu_config_output_dir(),
            cls.ert_model_dir(),
            cls.ert_distribution_dir(),
            cls.rms_field_dir(),
            cls.aps_model_export_dir(),
        ]
        err= False
        if cls.get_debug_level() >= Debug.VERY_VERBOSE:
            print(f"--- Current RMS project directory: {cls.project_dir()} ")
            print(f"--- Current working dir:           {str(Path().absolute())}  ")
        for p in file_paths:
            if not Path(p).exists():
                print(f"Error: In FMU mode, expect that this path or file exists: {p}")
                err = True
        if err:
            raise IOError("Can not find FMU file paths or directories.")
        return True

    @classmethod
    def _read_aps_config(cls)-> dict:
        # Read and validate existing aps config file
        print(f"Read configuration of FMU directories from file: {cls.config_file}  ")
        fmu_config = readYml(cls.config_file)

        missing_msg = []
        for key, value in cls.config_initial.items():
            if key not in fmu_config.keys():
                missing_msg.append(f"{key}")
                continue
            if isinstance(value, dict):
                for key2 in value.keys():
                    if key2 not in fmu_config[key].keys():
                        missing_msg.append(f"{key2} in {key}")

        if len(missing_msg) > 0:
            print("Error: The following keys or subkeys are not specified "
                  f"in file: {cls.config_file}")
            for msg in missing_msg:
                print(msg)
            raise ValueError(f"Missing keys in file {cls.config_file}")

        undefined_msg = []
        for key, value in fmu_config.items():
            if key not in cls.config_initial.keys():
                undefined_msg.append(f"{key}")
                continue
            if isinstance(value, dict):
                for key2 in value.keys():
                    if key2 not in cls.config_initial[key].keys():
                        undefined_msg.append(f"{key2} in {key}")
        if len(undefined_msg) > 0:
            print(f"Warning: The following keys are not defined and will be "
                  f"ignored in file: {cls.config_file}")
            for msg in undefined_msg:
                print(msg)
        return fmu_config

    @classmethod
    def _create_aps_config_file(cls):
        """
        Create aps_config file using standard FMU files and directories
        """
        print(" ")
        print(f"NOTE: File with configuration of standard FMU directories: {cls.config_file} will be created.")
        print("      If your FMU project use non-standard FMU directory structure or non-standard file name")
        print("      for global variables, please open and edit this file.")
        print(f"      Close and open again the APS job to be sure your modified configuration file: {cls.config_file} is used.")
        print(" ")
        with open(cls.config_file, 'w', encoding='utf-8') as file:
            file.write("# File in YAML format defining FMU directory structure and some file names\n")
            file.write("# When using standard FMU directory structure and file names,\n")
            file.write("# turn off using non-standard FMU settings in APS settings and this file will not be used.\n")
            file.write("# For FMU project using non-standard directory structure or alternative name for file with\n")
            file.write("# global variables, modify the settings here, but keep all keywords.\n")
            file.write("# Only file paths relevant for APS plugin is specified here.\n")

            for key, value in cls.config_initial.items():
                if isinstance(value, str):
                    file.write(f"{key.strip()}: {value.strip()}\n")
                elif isinstance(value, int):
                    file.write(f"{key.strip()}: {value}\n")
                elif isinstance(value, dict):
                    file.write(f"{key.strip()}:\n")
                    for key2, value2 in value.items():
                        file.write(f"    {key2.strip()}: {value2.strip()}\n")

        return copy.deepcopy(cls.config_initial)


if __name__ == "__main__":

    aps_config = APSConfig
    aps_config.init(project, use_config_file=True)
    config = aps_config.get_config()
    print(f"Config file:                    {aps_config.get_config_file()}")
    print(f"Top dir:                        {aps_config.top_dir()}  ")
    print(f"RMS model dir:                  {aps_config.rms_model_dir()}"  )
    print(f"Global var file:                {aps_config.global_variables_file()}")
    print(f"APS model export dir:           {aps_config.aps_model_export_dir()}  ")
    print(f"Ert dist dir:                   {aps_config.ert_distribution_dir()}"  )
    print(f"Ert model dir:                  {aps_config.ert_model_dir()}"  )
    print(f"fmu config input dir:           {aps_config.fmu_config_input_dir()} "  )
    print(f"fmu config output dir:          {aps_config.fmu_config_output_dir()} "  )
    print(f"rms field dir:                  {aps_config.rms_field_dir()} "  )
    print(f"rms field dir from runpath:     {aps_config.rms_field_dir_for_run_path()} "  )

    print(f"aps_param_master_extension:     {aps_config.fmu_master_config_extension()}")
    print(f"aps_param_extension:            {aps_config.fmu_config_extension()}")
    print(f"aps_ert_config_field_extension: {aps_config.ert_config_fields_extension()}")
    print(f"aps_ert_config_prob_extension:  {aps_config.ert_config_probs_extension()}")
    print(" ")



    print(f"Config: ")
    for key, value in config.items():

        if isinstance(value, dict):
            print(f"{key}:")
            for key2, value2 in value.items():
                print(f"   {key2}: {value2}")
        else:
            print(f"{key}: {value}")
