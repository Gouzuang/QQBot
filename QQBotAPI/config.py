import os

class CachePath:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Default cache paths
            cls._instance.image_cache = "./cache/images"
            cls._instance.voice_cache = "./cache/voices"
            cls._instance.temp_cache = "./cache/temp"
            cls._instance.data_cache = "./cache/data"
            
            # Create directories if they don't exist
            for path in [cls._instance.image_cache, 
                        cls._instance.voice_cache,
                        cls._instance.temp_cache,
                        cls._instance.data_cache]:
                if not os.path.exists(path):
                    os.makedirs(path)
                    
        return cls._instance
    
    def __init__(self):
        pass

    @property
    def image_path(self):
        return self.image_cache

    @property
    def voice_path(self):
        return self.voice_cache

    @property
    def temp_path(self):
        return self.temp_cache

    @property
    def data_path(self):
        return self.data_cache

    def set_image_path(self, path: str):
        self.image_cache = path

    def set_voice_path(self, path: str):
        self.voice_cache = path

    def set_temp_path(self, path: str):
        self.temp_cache = path

    def set_data_path(self, path: str):
        self.data_cache = path
        
class DataBasePath:
    def __init__(self):
        self._db_path = "./databases/"

    @property
    def db_path(self):
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        self._db_path = value
