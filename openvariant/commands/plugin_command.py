import click


@click.group(chain=True)
def cli_plugin():
    pass


@cli_plugin.command('plugin')
def plugin():
    pass


@cli_plugin.command(name="add", short_help='Generate the template to create a new plugin.')
@click.argument('plugin_name', type=click.STRING)
def add_plugin(plugin_name: str):
    print(plugin_name)
    pass
