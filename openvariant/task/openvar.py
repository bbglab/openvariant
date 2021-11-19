from os import cpu_count

import click as click

from openvariant.task.cat import cat as cat_task
from openvariant.task.count import count as count_task

from openvariant.task.groupby import group_by as group_by_task


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--debug', help='Show debug messages.', is_flag=True)
@click.version_option()
def cli(debug):
    # Configure the logging
    pass


@click.command(short_help='Concatenate files to standard input')
@click.argument('input_path', type=click.Path(exists=True), default='.')
# @click.option('--columns', '-c', multiple=True, type=click.STRING, help="Extra columns to add")
@click.option('--where', '-w', multiple=True, type=click.STRING, default=None, help="Filter expression. ie: "
                                                                                    "CHROMOSOME == 4")
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True))
@click.option('--header', help="Show the result header", is_flag=True)
def cat(input_path: str, where: str, annotations: str or None, header: bool):
    cat_task(input_path, annotations, where, header)


@click.command(short_help='Count number of variants')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--where', '-w', multiple=False, type=click.STRING)
@click.option('--groupby', '-g', type=click.STRING)
@click.option('--cores', help='Maximum processes to run in parallel.', type=click.INT, default=cpu_count())
@click.option('--quite', '-q', help="Don't show the progress, only the total count.", is_flag=True)
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True))
def count(input_path: str, where: str, groupby: str, cores: int, quite: bool, annotations: str or None):
    result = count_task(input_path, annotations, group_by=groupby, where=where, cores=cores, quite=quite)

    if len(result[1]) > 0:
        for k, v in sorted(result[1].items(), key=lambda v: v[1]):
            print("{}\t{}".format(k, v))

    print("TOTAL\t{}".format(result[0]))


@click.command(short_help='Groupby and run script')
@click.argument('input_path', type=click.Path(exists=True), default='.')
@click.option('--script', '-s', type=click.STRING)
@click.option('--where', '-w', multiple=True, type=click.STRING)
@click.option('--groupby', '-g', type=click.STRING)
@click.option('--cores', help='Maximum processes to run in parallel.', type=click.INT, default=cpu_count())
@click.option('--quite', '-q', help="Don't show the progress, only the total count.", is_flag=True)
@click.option('--annotations', '-a', default=None, type=click.Path(exists=True))
@click.option('--header', help='Send header as first row', is_flag=True)
@click.option('--show', help='Show group by each row', is_flag=True)
def groupby(input_path: str, script: str, where: str, groupby: str, cores: int, quite: bool, annotations: str,
            header: bool, show: bool):
    for group_key, group_result in group_by_task(input_path, annotations, script, key_by=groupby, where=where,
                                                 cores=cores, quite=quite, header=header):
        for r in group_result:
            if header:
                print(f"{r}")
                header = False
            else:
                print(f"{group_key}\t{r}") if show else print(f"{r}")


cli.add_command(cat)
cli.add_command(count)
cli.add_command(groupby)

if __name__ == "__main__":
    cli()
