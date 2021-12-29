from openvariant.plugins.plugin import Plugin


class BasicPlugin(Plugin):
    """
    Basic template of a customized plugin.
    This is a subclass of Plugin class, implemented inside OpenVariant.
    Use this files as a guidance to build new ones.
    """

    def run(self, row: dict) -> dict:
        return row
