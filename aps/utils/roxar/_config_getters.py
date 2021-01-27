from aps.utils.constants.simple import Debug


def get_debug_level(config: dict) -> Debug:
    try:
        return Debug(config['parameters']['debugLevel']['selected'])
    except KeyError:
        return Debug.VERY_VERBOSE
