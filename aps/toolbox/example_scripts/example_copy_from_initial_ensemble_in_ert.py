#!/usr/bin/env python

# Purpose: Copy field parameters from initial ensemble to updated ensemble.
#          This forward model can be used if for some reason the user doesn't want to
#          include all field parameters from APS into FIELD keywords in ERT,
#          but want to keep initial ensemble version of some of them instead.
#          Note: Application of this is a bit  "experimental" since the usual
#          way of handling GRF fields from APS is to update them all,
#          and not a subset of them in ERT with ES or ES-MDA.
# Written by: O.Lia
# Updated by: Therese Natterøy
import sys
import os
from pathlib import Path




def main():
    if len(sys.argv) != 3:
        print(
            "Usage: copy_fields_from_initial_ensemble  <iter>  <initial_fields_folder>"
        )
        raise IOError("Missing input")

    runpath = Path.cwd()
    print(f"Path: {runpath}")

    iter = int(sys.argv[1])
    fields_folder = sys.argv[2]
    initial_fields_folder = runpath.parent / "iter-0" / fields_folder

    print(f"ES-MDA Iteration number: {iter} ")
    if iter == 0:
        return

    initial_fields = [
        f.name for f in initial_fields_folder.glob("*") if f.suffix == ".roff"
    ]
    ert_fields = [field for field in initial_fields if (runpath / field).exists()]

    if ert_fields:
        for field_name in initial_fields:
            ert_field = runpath / field_name
            if field_name in ert_fields:
                print(f"Found ERT file {ert_field}. No need to do anything")
                continue

            print(
                f"Found no ERT file for {field_name}. Copying file from {initial_fields_folder} into runpath"
            )
            prev_iter_field = runpath.parent / f"iter-0/rms/output/aps" / field_name
            os.symlink(prev_iter_field, ert_field)
    else:
        print(f"Found no ERT FIELDS for APS, stopping the script...")


if __name__ == "__main__":
    main()
