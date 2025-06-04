from pathlib import Path

from pytest import fixture


@fixture
def data_directory():
    return Path(__file__).parent / 'data'


@fixture
def output_directory():
    directory = Path(__file__).parent / 'out'
    if not directory.exists():
        directory.mkdir(parents=True)
    return directory


@fixture
def attributes_file(output_directory):
    return output_directory / 'fmu_attributes.yaml'


@fixture
def output_model_file_name_1(output_directory):
    return output_directory / 'test_Trunc_output1.xml'


@fixture
def output_model_file_name_2(output_directory):
    return output_directory / 'test_Trunc_output2.xml'


@fixture
def out_poly_file_1(output_directory):
    return output_directory / 'test_Trunc_polygons1.dat'


@fixture
def out_poly_file_2(output_directory):
    return output_directory / 'test_Trunc_polygons2.dat'


@fixture
def cubic_gauss_field_files(data_directory):
    return [data_directory / 'cubic' / f'a{idx + 1}.dat' for idx in range(6)]


@fixture
def non_cubic_gauss_field_files(data_directory):
    return [data_directory / 'angle' / f'a{idx + 1}.dat' for idx in range(6)]


@fixture
def bayfill_gauss_field_files(data_directory):
    return [data_directory / 'bayfill' / f'a{idx + 1}.dat' for idx in range(3)]


@fixture
def facies_output_file_vectorized(output_directory):
    return output_directory / 'facies2D_vectorized.dat'


@fixture
def facies_output_file(output_directory):
    return output_directory / 'facies2D.dat'


@fixture
def facies_reference_file(case_number: int, data_directory, kind: str) -> Path:
    return data_directory / kind / f'test_case_{case_number}.dat'
