Coastline
=======================

Coastline is a command-line tool for managing various resources and
infrastructure used by our projects.

Thus far it only supports checking and creating Amazon SQS queues, but
it's planned to support Packer, Terraform, AWS EBS volumes and remote
admin tasks like initialising MongoDB replicasets.

In particular, the goal is to automate the flow of information (AMI
IDs, SQS queue URLs, instance IPs) between these tools so they can be
easily hooked together to build our infrastructure.

Installation
------------
Currently, it's recommended you create a Python virtualenv_ to install
the Coastline tool within.

After creating and activating the virtualenv, change into this directory
and run: ::

    python setup.py develop

This will install Coastline and any dependencies, and add the
command-line entry-point to the path. Using the ``develop`` command is
recommended so edits can be made to Coastline and seen immediately in
the virtualenv without reinstalling. (See the `Python Packaging Guide`_
and `setuptools docs`_ for more information on "development mode".)

After this, you can run the ``coastline`` command whenever you have the
virtualenv activated. To test, run ``coastline`` with no arguments: ::

    $ coastline
    Usage: coastline [OPTIONS] COMMAND [ARGS]...

    Options:
    -c, --config-path PATH
    -e, --env [development|staging|production]
    -s, --secrets-path PATH
    -S, --state-path PATH
    --help                          Show this message and exit.

    Commands:
    debug
    sqs

.. _virtualenv: https://virtualenv.pypa.io/en/latest/virtualenv.html
.. _Python Packaging Guide: http://python-packaging-user-guide.readthedocs.org/en/latest/tutorial.html#developing-your-project
.. _setuptools docs: http://pythonhosted.org/setuptools/setuptools.html#development-mode


Usage
-----

To use Coastline fully, you will also need a valid ``config.json``,
``state.json`` and ``secrets.json``. By default, these will be read from the
current working directory, but other paths can be specified with
command-line options.

Appropriate ``config.json`` and ``state.json`` files should be included in
your project's repo. The ``secrets.json`` contains per-user credentials and
*should not* be committed. To create your own, copy the
``secrets.json.example`` file to ``secrets.json`` in your project directory,
then edit the file to contain your own AWS access key ID and secret (see
`AWS IAM`_ to create these).

.. _AWS IAM: https://console.aws.amazon.com/iam/home

coastline sqs
~~~~~~~~~~~~~
Currently the only sub-command is ``coastline sqs``, for checking and
creating Amazon SQS queues.

Type ``coastline sqs`` for a list of available SQS sub-commands and usage.
