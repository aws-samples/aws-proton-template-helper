from . import jinja_helpers
from . import manifest
from . import proton_resources
import os
import questionary
import yaml
from operator import truediv
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.validation import Validator, ValidationError
from os.path import exists

def in_template():
    if "schema" in os.listdir('.'):
        return True
    return False


def is_service_template():
    with open("schema/schema.yaml", "r") as fh_:
        schema_yaml = yaml.safe_load(fh_)
    if "service_input_type" in schema_yaml["schema"]:
        return True
    return False


def service_template_contains_pipeline():
    return exists("pipeline_infrastructure")


def is_environment_template():
    with open("schema/schema.yaml", "r") as fh_:
        schema_yaml = yaml.safe_load(fh_)
    if "environment_input_type" in schema_yaml["schema"]:
        return True
    return False


class FileExistsValidator(Validator):
    def validate(self, document):
        if (exists(document.text) == False):
            raise ValidationError(message="Please enter a valid path to file",
                                  cursor_position=len(document.text))

def get_file(message):
    return questionary.text(message, completer=PathCompleter() ,validate=FileExistsValidator, validate_while_typing=False).ask()