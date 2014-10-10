from .. import di

@di.dependsOn('config')
@di.dependsOn('secrets')
def boto_module_connect_to_region(boto_module):
    config, secrets = di.resolver.unpack(boto_module_connect_to_region)
    return boto_module.connect_to_region(
            config['aws']['region'],
            aws_access_key_id=secrets['aws']['access_key_id'],
            aws_secret_access_key=secrets['aws']['secret_access_key'])

def vpc():
    import boto.vpc
    return boto_module_connect_to_region(boto.vpc)
    
def ec2():
    import boto.ec2
    return boto_module_connect_to_region(boto.ec2)
