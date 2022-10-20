import sys
import os

def excepthook(type, value, traceback):
    print("Error:")
    print(f"Type: {type.__name__}")
    print(f"{value}")

def run(project, **kwargs):
    sys.excepthook = excepthook
