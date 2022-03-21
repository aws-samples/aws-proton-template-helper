import questionary
import boto3
from questionary import Choice
from aws_proton_helper import helpers
from aws_proton_helper.helpers import manifest, jinja_helpers, proton_resources
from aws_proton_helper.compile import spec_helpers
from aws_proton_helper.compile.models import TemplateType, ResourceType
from botocore.exceptions import ClientError


def __get_remote_spec(template_type):
    proton_client = boto3.client('proton')
    environment_name = None
    service_name = None
    if template_type == TemplateType.ENVIRONMENT:
        environment_name = proton_resources.prompt_for_environment_name(proton_client)

        spec_text = proton_client.get_environment(name=environment_name)["environment"]["spec"]

    elif template_type == TemplateType.SERVICE:
        service_name = proton_resources.prompt_for_service_name(proton_client)
        
        spec_text = proton_client.get_service(name=service_name)["service"]["spec"]

    return (spec_text, environment_name, service_name)



def __get_inputs(template_text, template_type, resource_type):
    input_style = questionary.select("How do you want to provide your inputs?", 
                        choices=[
                            Choice(title='Supply local AWS Proton Spec File', value='local'),
                            Choice(title='Retrieve remote AWS Proton Spec File', value='remote'),
                            Choice(title='Parse my template for variable references (experimental)', value='parse')
                        ]).ask()
                        
    if input_style == "parse":
        all_variables = jinja_helpers.get_all_variables(template_text)
        return jinja_helpers.get_raw_inputs(all_variables)

    else:
        if input_style == "local":
            spec_file = helpers.get_file("Provide path to the spec file")
            with open(spec_file, 'r') as fh_:
                spec_text = fh_.read()
        elif input_style == "remote":
            spec_text, environment_name, service_name = __get_remote_spec(template_type)
        
        return spec_helpers.get_inputs_from_spec(spec_text, template_text, template_type, resource_type, environment_name, service_name)
    

def guided_compile():
    template_text = None
    template_type = None
    resource_type = None
    if helpers.in_template():
        cur_template = questionary.confirm("Hey! Looks like you're running this command inside of an AWS Proton Template. Is this one you want to work with?").ask()
        if cur_template:
            if helpers.is_environment_template():
                template_type = TemplateType.ENVIRONMENT
                resource_type = ResourceType.ENVIRONMENT
                cfn_file_path = manifest.get_cfn_file_path("infrastructure")
            elif helpers.is_service_template():
                template_type = TemplateType.SERVICE
                if not helpers.service_template_contains_pipeline():
                    resource_type = ResourceType.SERVICE_INSTANCE
                else:
                    resource_type = questionary.select("Looks like this is a Service Template. Are you testing the Service Instance or Pipeline?",
                                                    choices=[
                                                        Choice(title="Service Instance", value=ResourceType.SERVICE_INSTANCE),
                                                        Choice(title="Pipeline", value=ResourceType.SERVICE_PIPELINE)
                                                    ])

                if resource_type == ResourceType.SERVICE_INSTANCE:
                    cfn_file_path = manifest.get_cfn_file_path("instance_infrastructure")
                elif resource_type == ResourceType.SERVICE_PIPELINE:
                    cfn_file_path = manifest.get_cfn_file_path("pipeline_infrastructure")
    else:
        cont = questionary.confirm("Pro-tip: Run this inside of an AWS Proton Template Bundle for a smoother experience. Would you like to continue?").ask()
        if not cont:
            return
        
        template_type = questionary.select("What kind of AWS Proton Template are you testing?",
                                        choices=[
                                            Choice(title="Environment Template", value=TemplateType.ENVIRONMENT),
                                            Choice(title="Service Template", value=TemplateType.SERVICE)
                                        ]).ask()

        if template_type == TemplateType.SERVICE:
            resource_type = questionary.select("Are you testing the Service Instance or Pipeline?",
                                                choices=[
                                                    Choice(title="Service Instance", value=ResourceType.SERVICE_INSTANCE),
                                                    Choice(title="Pipeline", value=ResourceType.SERVICE_PIPELINE)
                                                ]).ask()
        else:
            resource_type = ResourceType.ENVIRONMENT

        cfn_file_path = helpers.get_file("Provide the path to your template file.")
        
    with open(cfn_file_path, 'r') as fh_:
        template_text = fh_.read()

    inputs = __get_inputs(template_text, template_type, resource_type)

    compiled_template = jinja_helpers.render_jinja(template_text, inputs)

    print(compiled_template)

    validate_conf = questionary.confirm("Would you like to validate that the compiled template is syntactically correct?").ask()

    if validate_conf:
        try:
            cfn_client = boto3.client('cloudformation')
            cfn_client.validate_template(TemplateBody=compiled_template)
            print("Valid CFN!")
        except ClientError as e:
            print(e)