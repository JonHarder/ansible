#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: pipenv

short_description: Module to make using pipenv declarative

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    name:
        description:
            - This is the message to send to the sample module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - language

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Install project dependancies from a Pipfile or Pipfile.lock
- name: Installing the dependancies
  pipenv:
    state: installed

# Update dependancies and update the lockfile to match
- name: Update the dependancies
  pipenv:
    state: updated

# Install a library, updating the Pipfile/Pipfile.lock as necessary
- name: Install requests
  pipenv:
    name: requests

# Install multiples libraries
- name: Install dependancies
  pipenv:
    name: "{{ item }}"
  with_items:
    - requests
    - flask
    - gunicorn

# Run a python script, this runs 'pipenv run python util.py arg1 arg2'
- name: Run a util script
  pipenv:
    script: "util.py arg1 arg2"

# Run a command, such as a binary which pipenv installed
- name: Run a command
  pipenv:
    run: "gunicorn app:app"
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule


def run_pipenv_command(module, *args):
    COMMAND = 'pipenv'
    args = [COMMAND, *args]
    output = module.run_command(args)
    if output[0]:
        module.fail_json(msg=output[2])
    else:
        return output[1]


def pipenv_install(module, result, name=None, dev=False):
    if name:
        output = run_pipenv_command(module, 'install', name)
    else:
        output = run_pipenv_command(module, 'install')
    result['changed'] = True
    return output, result


def pipenv_venv(module):
    return run_pipenv_command(module, '--venv')


def run_module():
    state_map = dict(
        present='install',
        latest='update',
        absent='uninstall'
    )

    module_args = dict(
        state=dict(type='str', default='present', choices=state_map.keys()),
        name=dict(type='str', required=False),
        script=dict(type='str', required=False),
        run=dict(type='str', required=False),
        venv=dict(type='bool', required=False),
        dev=dict(type='bool', default=False),
    )

    result = dict(
        changed=False,
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[['venv', 'state', 'name', 'script', 'run']],
        mutually_exclusive=[['venv', 'state'],
                            ['venv', 'name'],
                            ['venv', 'script'],
                            ['run', 'script'],
                           ]
    )

    state = module.params['state']
    name = module.params['name']
    venv = module.params['venv']
    dev = module.params['dev']

    if venv:
        result['message'] = pipenv_venv(module)
        module.exit_json(**result)

    if state == 'absent' and not name:
        module.fail_json(msg="'name' must be provided if 'state' is 'absent'", **result)

    output, result = pipenv_install(module, result, dev=dev)
    result['message'] = output

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
