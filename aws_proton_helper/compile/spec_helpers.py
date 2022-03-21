from os import environ
import yaml
import questionary
import boto3
from aws_proton_helper.helpers import jinja_helpers, proton_resources
from aws_proton_helper.compile.models import TemplateType, ResourceType

def __get_env_spec_inputs(spec_yaml, environment_name=None):
    inputs = {}
    inputs["environment"] = {}
    inputs["environment"]["inputs"] = spec_yaml["spec"]

    if environment_name is None:
        inputs["environment"]["name"] = questionary.text("Enter environment name", 
                                                      validate=lambda text: len(text) > 0,
                                                      validate_while_typing=False).ask()
    else:
        inputs["environment"]["name"] = environment_name

    return inputs


def __get_service_input(all_variables, service_name=None):
    inputs = {}
    service_source = questionary.select("It looks like your template relies on some variables from a Proton Service. How would you like to provide those values",
                                            choices=["Retrieve outputs from AWS Proton for the service",
                                                        "Provide inputs from inferred schema"]).ask()
    if service_source == "Provide inputs from inferred schema":
        inputs = jinja_helpers.get_raw_input(all_variables["service"], "service")
    else:
        proton_client = boto3.client('proton')
        if service_name is None:
            service_name = proton_resources.prompt_for_service_name(proton_client)
        inputs = proton_client.get_service(name=service_name)['service']

    return inputs



def __get_instance_input(instance, all_variables):
    inputs = {}
    inputs["environment"] = {}
    inputs["environment"]["name"] = instance["environment"]
    if "environment" in all_variables:
        environment_source = questionary.select("It looks like your template relies on some variables from a Proton Environment. How would you like to provide those values",
                                                choices=["Retrieve outputs from AWS Proton for environment: " + instance["environment"],
                                                            "Provide inputs from inferred schema"]).ask()
        if environment_source == "Provide inputs from inferred schema":
            inputs["environment"] = jinja_helpers.get_raw_input(all_variables["environment"], "environment")
        else:
            proton_client = boto3.client('proton')
            outputs = proton_client.list_environment_outputs(environmentName=instance["environment"])["outputs"]
            output_dict = {}
            for output in outputs:
                output_dict[output["key"]] = output["valueString"]
            inputs["environment"]["outputs"] = output_dict
            

    inputs["service_instance"] = {}
    inputs["service_instance"]["name"] = instance["name"]
    inputs["service_instance"]["inputs"] = instance["spec"]
    return inputs


def __get_svc_spec_inputs(spec_yaml, template, resource_type, service_name=None):
    options = []
    for instance in spec_yaml["instances"]:
        options.append(instance["name"])

    all_variables = jinja_helpers.get_all_variables(template)
    inputs = {}
    if "service" in all_variables:
        inputs["service"] = __get_service_input(all_variables, service_name)

    if resource_type == ResourceType.SERVICE_PIPELINE:
        inputs["pipeline"] = {}
        inputs['pipeline']['inputs'] = spec_yaml['pipeline']
        instance_inputs = []
        for instance in spec_yaml["instances"]:
            instance_input = __get_instance_input(instance, all_variables)
            translated_input = instance_input["service_instance"]
            if "environment" in instance_input:
                translated_input["environment"] = instance_input["environment"]
            instance_inputs.append(translated_input)
        inputs["service_instances"] = instance_inputs
        return inputs
    else:
        selected_instance = questionary.select("Which instance would you like to compile?", choices=options).ask()
        for instance in spec_yaml["instances"]:
            if instance["name"] == selected_instance:
                instance_input = __get_instance_input(instance, all_variables)
                inputs["service_instance"] = instance_input["service_instance"]
                if "environment" in instance_input:
                    inputs["environment"] = instance_input["environment"]
                return inputs


def get_inputs_from_spec(spec_text, template, template_type, resource_type, environment_name=None, service_name=None):
    spec_yaml = yaml.safe_load(spec_text)
    if template_type == TemplateType.ENVIRONMENT:
        if spec_yaml["proton"] != "EnvironmentSpec":
            questionary.print("Invalid spec, must be an EnvironmentSpec")
            raise
        return __get_env_spec_inputs(spec_yaml, environment_name)
    elif template_type == TemplateType.SERVICE:
        if spec_yaml["proton"] != "ServiceSpec":
            questionary.print("Invalid spec, must be a ServiceSpec")
            raise
        return __get_svc_spec_inputs(spec_yaml, template, resource_type, service_name)
    else:
        print("Unexpected spec type, unable to get inputs: " + spec_yaml["proton"])
        raise