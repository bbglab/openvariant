class Plugin(object):
    """
    Base class that each plugin must inherit from.
    """

    def run(self, argument):
        """
        This is a main function (required) which OpenVariant will call every time that this plugin is
        described in an annotation file.
        """
        raise NotImplementedError
