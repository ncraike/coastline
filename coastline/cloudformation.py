from coastline import di
from coastline.aws.connections import cloudformation as connect

def update(stack_name, template_body):
    stack_id = connect().update_stack(
            stack_name,
            template_body=template_body)
    return stack_id

def get_stack_events(stack_name_or_id, next_token=None):
    conn = connect()
    result = conn.describe_stack_events(stack_name_or_id)

    from IPython import embed; embed()
