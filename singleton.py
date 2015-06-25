class Singleton(type):
    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

    def __getattribute__(self, name):
        if name =='instance':
            return super(Singleton, self).__getattribute__(name)

        return self().__getattribute__(name)
