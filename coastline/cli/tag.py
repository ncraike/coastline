import click

from .. import di
from .. import tag

cli = click.Group('tag')

OK_COLOR = 'green'
WARN_COLOR = 'yellow'
ERR_COLOR = 'red'

TAG_STATUS_COLORS = {
        tag.TagStatus.correct: OK_COLOR,
        tag.TagStatus.incorrect: ERR_COLOR,
        tag.TagStatus.missing: ERR_COLOR,
        }

def tags_with_status(tags, desired_status):
    return [tag_name
            for tag_name, tag_status in tags.items()
            if tag_status == desired_status]

def describe_tags_status(tags_status):
    output = []
    for status_name, status in (
            ('missing', tag.TagStatus.missing),
            ('incorrect', tag.TagStatus.incorrect),
            ('correct', tag.TagStatus.correct)):

        matching_tags = tags_with_status(tags_status, status)
        if not matching_tags:
            continue

        color = TAG_STATUS_COLORS[status]
        output_str = '{n} tags {status_name}'.format(
                n=len(matching_tags),
                status_name=status_name)
        output.append(
                click.style(output_str, fg=color))

    return ', '.join(output)

def tags_not_correct_by_inst(instances_tags_status):
    return {
            inst: [
                tag_name for tag_name, tag_status in tags.items()
                if tag_status is not tag.TagStatus.correct]
            for inst, tags in instances_tags_status.items()}

def inst_with_tags_not_correct(instances_tags_status):
    return [inst for inst, tags
            in tags_not_correct_by_inst(instances_tags_status).items()
            if len(tags)]

def tags_not_correct(instances_tags_status):
    return sum(
            tags_not_correct_by_inst(instances_tags_status).values(), [])

@cli.command()
def check():
    tags = tag.get_required_tags()
    instances = tag.get_instances_for_config()
    instances_tags_status = tag.get_instances_tags_status(instances, tags)

    for inst in instances:
        click.echo('Instance: {}'.format(inst.id))
        inst_name = inst.tags.get('Name')
        if inst_name:
            click.echo('    Name: {}'.format(inst_name))
        inst_descript = inst.tags.get('Description')
        if inst_descript:
            click.echo('    Description: {}'.format(inst_descript))

        tags_status = instances_tags_status[inst]
        click.echo(describe_tags_status(tags_status))

        click.echo()

    inst_need_tagging = inst_with_tags_not_correct(instances_tags_status)
    tags_to_apply = tags_not_correct(instances_tags_status) 

    if inst_need_tagging or tags_to_apply:
        click.secho(
                '{} instances need tagging \n'
                '{} tags total need to be applied'.format(
                    len(inst_need_tagging), len(tags_to_apply)),
                fg=WARN_COLOR)
    else:
        click.secho('No tagging needed', fg=OK_COLOR)

@cli.command()
def apply():
    tags = tag.get_required_tags()
    instances = tag.get_instances_for_config()
    instances_tags_status = tag.get_instances_tags_status(instances, tags)
    inst_need_tagging = inst_with_tags_not_correct(instances_tags_status)
    for inst in inst_need_tagging:
        click.echo('Adding tags for {}'.format(inst.id))
        inst.add_tags(tags)
