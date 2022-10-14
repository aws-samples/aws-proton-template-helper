# AWS Proton Helper
Collection of helper tools for interacting with AWS Proton templates

# Installation
## Requirements
* python3 (requires 3.7+)
* pip: https://pip.pypa.io/en/stable/installation/

On Ubuntu/Debian systems, you may also need to install the following packages:
```
> sudo apt-get install python3-venv python3-wheel -y
```

## Set Up Your Virtual Environment
Virtual environments are recommended when working with python as it can become easy to mix up dependencies when globally managing them.

### Create the virtual environment
```
> python -m venv env
```

### Activate the virtual environment
Once you activate your virtual environment, this will scope all future `pip` install to that environment.

```
# Mac
# > source env/Scripts/activate

# Linux
# > source env/bin/activate

# Windows
# > .\env\Scripts\Activate.ps1
```

### Deactivate the virtual environment
Deactivating your virtual environment will reset to your standard shell. You will no longer have access to anything installed inside of the virtual environment.

```
> deactivate
```

## Install
```
> pip install .
```

If you see an error like `invalid command 'bdist_wheel'`, try the following:
```
pip install wheel
pip install --upgrade --no-deps --force-reinstall aws-proton-helper
```

# Usage
Just type the following and the command will walk you through the rest.
```
> aws-proton-helper
```

## Common Workflows
### Validating Template Changes Before Updating
In this scenario you have a pre-existing tempalte that's already registered in AWS Proton and an instance of that template deployed in your account.
![demo](assets/record.gif)

## Windows
I'm not very well versed in windows development so this may not be the most efficient way, feel free to submit a PR with better instructions if you know them.

This assumes you have the [windows python launcher](https://docs.python.org/3/using/windows.html) set up and also that you are in the virtual environment we set up above.

```
> py env\Scripts\aws-proton-helper
```

You can also create a function in your powershell profile so that you don't have to remember the path every time.

```
function proton-helper { py C:\PATH\TO\env\Scripts\aws-proton-helper }
```

# TODO
* This is currently very coupled to Cloudformation + Jinja, that should be abstracted out

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
