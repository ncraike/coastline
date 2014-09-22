from .. import di

import subprocess

def plan(working_dir):
    tf_call = subprocess.Popen(
            ['terraform', 'plan'],
            stdout=subprocess.PIPE,
            cwd=working_dir)

    for line in tf_call.stdout:
        print(
                line.decode('utf8'),
                end='')
        #output = line.decode('utf8')
        #if output.strip():
        #    blankline_count = 0
        #else:
        #    blankline_count += 1

        #print(output, end='')

        #if blankline_count > 3:
        #    return
