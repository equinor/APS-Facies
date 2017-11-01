def normalize_number(
        value: float, minimum_in: float, maximum_in: float, minimum_out: float, maximum_out: float
) -> float:
    # TODO: Write unit test(s)
    value = truncate_number(minimum_in, value, maximum_in)
    normalized = (value - minimum_in) / (maximum_in - minimum_in)
    normalized *= (maximum_out - minimum_out) + minimum_out
    normalized = truncate_number(minimum_out, normalized, maximum_out)
    return normalized


def truncate_number(minimum: float, value: float, maximum: float) -> float:
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
