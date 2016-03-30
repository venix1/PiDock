"""Export Singleton metaclass."""


class Singleton(type):
    """metaclass used to allow only single instance of class to exist."""

    def __init__(self, *args, **kwargs):
        """construct instance and pass arguments."""
        super(Singleton, self).__init__(*args, **kwargs)
        self.instance = None

    def __call__(self, *args, **kwargs):
        """Return instance class or create one."""
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

    def __getattribute__(self, name):
        """Forward all attribute lookups to instance."""
        if name == 'instance':
            return super(Singleton, self).__getattribute__(name)

        return self().__getattribute__(name)
