from aps.algorithms.APSModel import APSModel
from aps.utils.constants.simple import Debug

def run(project, model_file, output_model_file=None, debug_level=Debug.READ, **kwargs):
    aps_model = APSModel(model_file,debug_level=debug_level)
    if debug_level == Debug.READ:
        debug_level = aps_model.debug_level
    aps_model.check_active_cells(project, debug_level=debug_level)
    if output_model_file is not None:
        print(f"Write file:{output_model_file} ")
        aps_model.write_model(output_model_file)

if __name__ == "__main__":
    # Test example
    aps_model_file = "APS.xml"
    out_model_file = "APS_out.xml"
    debug_level = Debug.READ
    run(project, model_file=aps_model_file, output_model_file=out_model_file, debug_level=debug_level)
