# AWS Proton Helper
Unofficial collection of helper tools for interacting with AWS Proton

# Installation
## Requirements
* python3+ (recommended 3.3+)
* pip: https://pip.pypa.io/en/stable/installation/

## Set Up Your Virtual Environment
Virtual environments are recommended when working with python as it can become easy to mix up dependencies when globally managing them.

### Create the virtual environment
```
# python3.3+
> python -m venv env #venv comes prebundled with python3.3+, no need to install

# < python3.3
> python3 -m pip install --user virtualenv
> python -m virtualenv env
```

### Activate the virtual environment
Once you activate your virtual environment, this will scope all future `pip` install to that environment. 

```
# Same for all versions
# Mac/Linux
# > source env/Scripts/activate

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
> pip install aws-proton-helper
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