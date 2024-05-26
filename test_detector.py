import random

from ai_detector_helpers import ai_detector_server


def simple_ai_detector(string):
    return random.random()


ai_detector_server(simple_ai_detector)
