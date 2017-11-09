def normalize_number(
        value: float, minimum_in: float, maximum_in: float, minimum_out: float, maximum_out: float
) -> float:
    # TODO: Write unit test(s)
    if isinstance(value, str):
        value = float(value)
    value = truncate_number(minimum_in, value, maximum_in)
    normalized = (value - minimum_in) / (maximum_in - minimum_in)
    normalized *= (maximum_out - minimum_out) + minimum_out
    normalized = truncate_number(minimum_out, normalized, maximum_out)
    return normalized


def truncate_number(minimum: float, value: float, maximum: float) -> float:
    if float(value) < minimum:
        return minimum
    elif float(value) > maximum:
        return maximum
    else:
        return value


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def strip_trailing_decimals(number, maximum_number_of_decimals: int) -> str:
    assert isinstance(number, float) or isinstance(number, int) or isinstance(number, str)
    numeric_string = str(number)
    if maximum_number_of_decimals < 0 or isinstance(number, int):
        # Nothing to be done
        return numeric_string
    elif '.' in numeric_string:
        return numeric_string[:numeric_string.find('.') + maximum_number_of_decimals]
    else:
        return numeric_string
