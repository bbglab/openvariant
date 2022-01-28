from os import cpu_count
import click as click

import openvariant
from openvariant.commands.tasks.cat import cat as cat_task
from openvariant.commands.tasks.count import count as count_task
from openvariant.commands.tasks.groupby import group_by as group_by_task
from openvariant.commands.tasks.plugin import PluginActions


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(openvariant.__version__)
def openvar():
    """'openvar' is the command-line interface of OpenVariant.
    Parsing and data transformation of multiple input formats."""
    pass


@openvar.command(name="cat", short_help='Concatenate files to standard input')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--where', '-w', type=click.STRING, default=None, help="Filter expression. eg: CHROMOSOME == 4")
@click.option('--annotations', '-a', type=click.Path(exists=True), default=None)
@click.option('--header', help="Show the result header", is_flag=True)
def cat(input_path: str, where: str or None, annotations: str or None, header: bool):
    """Print the parsed files on the stdout."""
    cat_task(input_path, annotations, where, header)


@openvar.command(name="count", short_help='Number of rows that matches a specified criterion')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--where', '-w', multiple=False, type=click.STRING, help="Filter expression. eg: CHROMOSOME == 4")
@click.option('--group_by', '-g', type=click.STRING, help="Filter expression. eg: CHROMOSOME")
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True))
@click.option('--cores', '-c', help='Maximum processes to run in parallel.', type=click.INT, default=cpu_count())
@click.option('--quite', '-q', help="Don't show the progress, only the total count.", is_flag=True)
def count(input_path: str, where: str, group_by: str, cores: int, quite: bool, annotations: str or None) -> None:
    """Print on the stdout the number of rows that meets the criteria."""
    result = count_task(input_path, annotations, group_by=group_by, where=where, cores=cores, quite=quite)
    if len(result[1]) > 0:
        for k, v in sorted(result[1].items(), key=lambda res: res[1]):
            print("{}\t{}".format(k, v))

    print("TOTAL\t{}".format(result[0]))


@openvar.command(name="groupby", short_help='Groups rows that have the same values into summary rows')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--header', help='Send header as first row', is_flag=True)
@click.option('--show', help='Show group by each row', is_flag=True)
@click.option('--group_by', '-g', type=click.STRING, default=None, help="Filter expression. eg: CHROMOSOME")
@click.option('--where', '-w', type=click.STRING, default=None, help="Filter expression. eg: CHROMOSOME == 4")
@click.option('--script', '-s', type=click.STRING, default=None,
              help="Filter expression. eg: gzip > \${GROUP_KEY}.parsed.tsv.gz")
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True))
@click.option('--cores', '-c', help='Maximum processes to run in parallel.', type=click.INT, default=cpu_count())
@click.option('--quite', '-q', help="Don't show the progress, only the total count.", is_flag=True)
def groupby(input_path: str, script: str, where: str, group_by: str, cores: int, quite: bool, annotations: str or None,
            header: bool, show: bool):
    """Print on the stdout the parsed files group by a specified field."""
    for group_key, group_result, command in group_by_task(input_path, annotations, script, key_by=group_by, where=where,
                                                          cores=cores, quite=quite, header=header):
        for r in group_result:
            if command:
                print(f"{group_key}\t{r}") if show else print(f"{r}")
            else:
                if header:
                    print(f"{r}")
                    header = False
                else:
                    print(f"{group_key}\t{r}") if show else print(f"{r}")


@openvar.command(name="plugin", short_help='Actions to execute for a plugin: create')
@click.argument('action', type=click.Choice(['create']))
@click.option('--name', '-n', type=click.STRING)
@click.option('--directory', '-d', type=click.STRING)
def plugin(action, name: str or None, directory: str or None):
    """Actions to apply on the plugin system."""
    PluginActions[action.upper()].value(name, directory)


if __name__ == "__main__":
    openvar()
