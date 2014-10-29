import click

from coastline import di
from coastline import cloudformation

cli = click.Group('cloudformation')

@cli.command()
@click.argument('stack_name')
@click.argument('template_file', type=click.File('r'))
def update(stack_name, template_filename):
    template_body = template_filename.read()
    cloudformation.update(stack_name, template_body)

@cli.command()
@click.argument('stack_name')
def events(stack_name):
    cloudformation.get_stack_events(stack_name)
