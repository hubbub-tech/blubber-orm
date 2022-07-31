from .config import Config

class UIDGenerator:

    _instance = None

    def __init__(self):
        if UIDGenerator._instance:
            #TODO: log that this problem happened
            raise Exception("UIDGenerator instance should only be created once.")
        else:
            UIDGenerator._instance = Config.DEFAULT_CUSTOM_EPOCH


    @staticmethod
    def get_instance():
        if UIDGenerator._instance is None:
            UIDGenerator()
        return UIDGenerator._instance
