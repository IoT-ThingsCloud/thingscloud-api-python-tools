class GlobalStore:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
        return cls._instance
    def set_variable(self, key, value):
        self.data[key] = value
    def get_variable(self, key):
        return self.data.get(key)