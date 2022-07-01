from os import cpu_count
import click as click

import openvariant
from openvariant.tasks.cat import cat as cat_task
from openvariant.tasks.count import count as count_task
from openvariant.tasks.groupby import group_by as group_by_task
from openvariant.tasks.plugin import PluginActions


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(openvariant.__version__)
def openvar():
    """'openvar' is the command-line interface of OpenVariant.
    Parsing and data transformation of multiple input formats."""
    pass


@openvar.command(name="cat", short_help='Concatenate parsed files to standard output.')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--where', '-w', type=click.STRING, default=None, help="Condition expression. eg: CHROMOSOME == 4")
@click.option('--annotations', '-a', type=click.Path(exists=True), default=None,
              help="Annotation path. eg: /path/annotation.yaml")
@click.option('--header', is_flag=True, help="Show the result header.")
@click.option('--output', '-o', default=None, help="File to write the output.")
def cat(input_path: str, where: str or None, annotations: str or None, header: bool, output: str or None):
    """Print the parsed files on the stdout/"output"."""
    cat_task(input_path, annotations, where, header, output)


@openvar.command(name="count", short_help='Number of rows that matches a specified criterion.')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--where', '-w', multiple=False, type=click.STRING, help="Condition expression. eg: CHROMOSOME == 4")
@click.option('--group_by', '-g', type=click.STRING, help="Key to group rows. eg: COUNTRY")
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True),
              help="Annotation path. eg: /path/annotation.yaml")
@click.option('--cores', '-c', type=click.INT, default=cpu_count(), help='Maximum processes to run in parallel.')
@click.option('--quite', '-q', is_flag=True, help="Don't show the progress.")
@click.option('--output', '-o', default=None, help="File to write the output.")
def count(input_path: str, where: str, group_by: str, cores: int, quite: bool, annotations: str or None,
          output: str or None) -> None:
    """Print on the stdout/"output" the number of rows that meets the criteria."""
    result = count_task(input_path, annotations, group_by=group_by, where=where, cores=cores, quite=quite)
    out_file = None
    if output:
        out_file = open(output, "w")
    if len(result[1]) > 0:
        for k, v in sorted(result[1].items(), key=lambda res: res[1]):
            if output:
                out_file.write("{}\t{}\n".format(k, v))
            else:
                print("{}\t{}".format(k, v))

    if output:
        out_file.write("TOTAL\t{}\n".format(result[0]))
    else:
        print("TOTAL\t{}".format(result[0]))

    if output:
        out_file.close()


@openvar.command(name="groupby", short_help='Group the parsed result for each different value of the specified key.')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--header', is_flag=True, help="Show the result header.")
@click.option('--show', is_flag=True, help='Show group by each row.')
@click.option('--where', '-w', type=click.STRING, default=None, help="Filter expression. eg: CHROMOSOME == 4")
@click.option('--group_by', '-g', type=click.STRING, default=None, help="Key to group rows. eg: COUNTRY")
@click.option('--script', '-s', type=click.STRING, default=None,
              help="Filter expression. eg: gzip > \${GROUP_KEY}.parsed.tsv.gz")
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True),
              help="Annotation path. eg: /path/annotation.yaml")
@click.option('--cores', '-c', type=click.INT, default=cpu_count(), help='Maximum processes to run in parallel.')
@click.option('--quite', '-q', is_flag=True, help="Don't show the progress.")
@click.option('--output', '-o', help="File to write the output.", default=None)
def groupby(input_path: str, script: str, where: str, group_by: str, cores: int, quite: bool, annotations: str or None,
            header: bool, show: bool, output: str or None):
    """Print on the stdout/"output" the parsed files group by a specified field."""
    out_file = None
    if output:
        out_file = open(output, 'w')
    for group_key, group_result, command in group_by_task(input_path, annotations, script, key_by=group_by, where=where,
                                                          cores=cores, quite=quite, header=header):
        for r in group_result:
            if command:
                if output:
                    out_file.write(f"{group_key}\t{r}\n") if show else out_file.write(f"{r}\n")
                else:
                    print(f"{group_key}\t{r}") if show else print(f"{r}")
            else:
                if header:
                    if output:
                        out_file.write(f"{r}\n")
                    else:
                        print(f"{r}")
                    header = False
                else:
                    if output:
                        out_file.write(f"{group_key}\t{r}\n") if show else out_file.write(f"{r}\n")
                    else:
                        print(f"{group_key}\t{r}") if show else print(f"{r}")
    if output:
        out_file.close()


@openvar.command(name="plugin", short_help='Actions to execute for a plugin: create.')
@click.argument('action', type=click.Choice(['create']))
@click.option('--name', '-n', type=click.STRING, help="Name of the plugin.")
@click.option('--directory', '-d', type=click.STRING, help="Directory to reach the plugin.")
def plugin(action, name: str or None, directory: str or None):
    """Actions to apply on the plugin system."""
    PluginActions[action.upper()].value(name, directory)


if __name__ == "__main__":
    openvar()
