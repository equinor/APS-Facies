from PyQt5.QtWidgets import QSlider


def get_value_of_slider(sender: QSlider) -> int:
    if isinstance(sender, QSlider):
        return sender.value()
    else:
        raise TypeError
