import json
import questionary
import os
import yaml
from aws_proton_helper import helpers
from aws_proton_helper.compile.models import TemplateType
from openapi_core import create_spec
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.validators import RequestValidator
from openapi_spec_validator import validate_spec
import pkg_resources

BASE_OPEN_API_SPEC_FILE = {
    TemplateType.ENVIRONMENT: 'environment-base.yaml',
    TemplateType.SERVICE: 'service-base.yaml',
    TemplateType.SERVICE_WITHOUT_PIPELINE: 'service-base.yaml'
}

# References in the template bundle schema like: $ref: "#/PipelineStage"
# become: $ref: "#/components/schemas/PipelineStage"
def __convert_template_schema_references_to_openapi_spec(element):
    if isinstance(element, dict):
        if '$ref' in element:
            element['$ref'] = __convert_template_schema_reference_string_to_openapi_spec(element['$ref'])

        for child_element in element.values():
            __convert_template_schema_references_to_openapi_spec(child_element)
    elif isinstance(element, list):
        for child_element in element:
            __convert_template_schema_references_to_openapi_spec(child_element)

# "#/PipelineStage" ==> "#/components/schemas/PipelineStage"
def __convert_template_schema_reference_string_to_openapi_spec(ref_value):
    return '#/components/schemas' + ref_value[1:]

# References in the template bundle schema like: $ref: "#/components/schemas/PipelineStage"
# become: $ref: "#/PipelineStage"
def __convert_openapi_spec_references_to_template_schema(element):
    if isinstance(element, dict):
        if '$ref' in element:
            element['$ref'] = __convert_openapi_reference_string_to_template_schema(element['$ref'])
        element.pop('x-scope', None)

        for child_element in element.values():
            __convert_openapi_spec_references_to_template_schema(child_element)
    elif isinstance(element, list):
        for child_element in element:
            __convert_openapi_spec_references_to_template_schema(child_element)

# "#/components/schemas/PipelineStage" ==> "#/PipelineStage"
def __convert_openapi_reference_string_to_template_schema(ref_value):
    return ref_value.replace('/components/schemas', '')

def __convert_template_schema_to_openapi_spec(template_bundle_dir):
    with open(os.path.join(template_bundle_dir, 'schema', 'schema.yaml'), 'r') as fh_:
        schema_yaml = yaml.safe_load(fh_)

    if schema_yaml['schema']['format']['openapi'] != '3.0.0':
        questionary.print('Invalid schema, does not specify OpenAPI 3.0.0 as the schema format')
        raise

    template_type = None
    if 'service_input_type' in schema_yaml['schema']:
        if 'pipeline_input_type' in schema_yaml['schema']:
            template_type = TemplateType.SERVICE
        else:
            template_type = TemplateType.SERVICE_WITHOUT_PIPELINE
    elif 'environment_input_type' in schema_yaml['schema']:
        template_type = TemplateType.ENVIRONMENT
    else:
        questionary.print('Invalid schema, could not find service_input_type or environment_input_type')
        raise

    base_spec_stream = pkg_resources.resource_stream(__name__, os.path.join('openapi_base_specs', BASE_OPEN_API_SPEC_FILE[template_type]))
    openapi_spec = yaml.safe_load(base_spec_stream)

    # Fill in references to the main input types defined in the template bundle schema
    if template_type == TemplateType.ENVIRONMENT:
        env_input_ref = {'$ref': "#/components/schemas/{}".format(schema_yaml['schema']['environment_input_type'])}
        openapi_spec['components']['schemas']['TemplateInputs']['properties']['spec'] = env_input_ref

    if template_type == TemplateType.SERVICE_WITHOUT_PIPELINE or template_type == TemplateType.SERVICE:
        service_input_ref = {'$ref': "#/components/schemas/{}".format(schema_yaml['schema']['service_input_type'])}
        openapi_spec['components']['schemas']['ServiceInstanceInputs']['properties']['spec'] = service_input_ref

    if template_type == TemplateType.SERVICE:
        pipeline_input_ref = {'$ref': "#/components/schemas/{}".format(schema_yaml['schema']['pipeline_input_type'])}
        openapi_spec['components']['schemas']['TemplateInputs']['properties']['pipeline'] = pipeline_input_ref
        required_props = openapi_spec['components']['schemas']['TemplateInputs']['required']
        required_props.append('pipeline')

    # Insert types defined in the template bundle schema into the OpenAPI spec
    for type_name, type_def in schema_yaml['schema']['types'].items():
        __convert_template_schema_references_to_openapi_spec(type_def)
        openapi_spec['components']['schemas'][type_name] = type_def

    return openapi_spec

# Wrap the Proton template bundle schema into a full OpenAPI specification and validate the given spec file against it
def validate_spec_against_template_schema():
    template_bundle_dir = None

    if helpers.in_template():
        cur_template = questionary.confirm("Hey! Looks like you're running this command inside of an AWS Proton Template. Is this one you want to work with?").ask()
        if cur_template:
            template_bundle_dir = os.getcwd()
    else:
        cont = questionary.confirm('Pro-tip: Run this inside of an AWS Proton Template Bundle for a smoother experience. Would you like to continue?').ask()
        if not cont:
            return

    if template_bundle_dir is None:
        template_bundle_dir = helpers.get_file('Provide the path to your template bundle directory.')

    proton_spec_file = helpers.get_file('Provide the path to your Proton spec file.')
    with open(proton_spec_file, 'r') as fh_:
        proton_spec_contents = yaml.safe_load(fh_)

    openapi_spec_dict = __convert_template_schema_to_openapi_spec(template_bundle_dir)
    validate_spec(openapi_spec_dict)
    openapi_spec = create_spec(openapi_spec_dict)
    validator = RequestValidator(openapi_spec)

    request = OpenAPIRequest(
        full_url_pattern='https://localhost:8000/proton-spec',
        method='put',
        body=json.dumps(proton_spec_contents),
        mimetype='application/json',
    )

    result = validator.validate(request)
    result.raise_for_errors()
    questionary.print('The spec file is valid against the template schema')

# Wrap the Proton template bundle schema into a full OpenAPI specification, validate it, write it to a file
def convert_template_schema_to_openapi_spec(outputToFile=True):
    template_bundle_dir = None

    if helpers.in_template():
        cur_template = questionary.confirm("Hey! Looks like you're running this command inside of an AWS Proton Template. Is this one you want to work with?").ask()
        if cur_template:
            template_bundle_dir = os.getcwd()
    else:
        cont = questionary.confirm('Pro-tip: Run this inside of an AWS Proton Template Bundle for a smoother experience. Would you like to continue?').ask()
        if not cont:
            return

    if template_bundle_dir is None:
        template_bundle_dir = helpers.get_file('Provide the path to your template bundle directory.')

    openapi_spec = __convert_template_schema_to_openapi_spec(template_bundle_dir)

    # Write out the OpenAPI spec to a file
    if outputToFile:
        output_file = os.path.join(template_bundle_dir, 'schema', 'openapi-spec.generated.yaml')
        with open(output_file, 'w') as fh_:
            yaml.dump(openapi_spec, fh_)
        questionary.print("Generated OpenAPI 3.0 specification file is located at {}".format(output_file))

    # Validate the OpenAPI specification
    validate_spec(openapi_spec)

    if not outputToFile:
        questionary.print('The template bundle schema file is valid')

    return openapi_spec

# Convert an OpenAPI specification generated by this module back into a template bundle schema file
def convert_openapi_spec_to_template_schema():
    template_bundle_dir = None

    if helpers.in_template():
        cur_template = questionary.confirm("Hey! Looks like you're running this command inside of an AWS Proton Template. Is this one you want to work with?").ask()
        if cur_template:
            template_bundle_dir = os.getcwd()
    else:
        cont = questionary.confirm('Pro-tip: Run this inside of an AWS Proton Template Bundle for a smoother experience. Would you like to continue?').ask()
        if not cont:
            return

    if template_bundle_dir is None:
        template_bundle_dir = helpers.get_file('Provide the path to your template bundle directory.')

    with open(os.path.join(template_bundle_dir, 'schema', 'openapi-spec.generated.yaml'), 'r') as fh_:
        openapi_spec = yaml.safe_load(fh_)
    validate_spec(openapi_spec)

    with open(os.path.join(template_bundle_dir, 'schema', 'schema.yaml'), 'r') as fh_:
        existing_template_schema = yaml.safe_load(fh_)

    new_template_schema = {
        'schema': {
            'format': {
                'openapi': '3.0.0'
            },
            'types': {}
        }
    }

    template_type = None
    if 'service_input_type' in existing_template_schema['schema']:
        if 'pipeline_input_type' in existing_template_schema['schema']:
            template_type = TemplateType.SERVICE
        else:
            template_type = TemplateType.SERVICE_WITHOUT_PIPELINE
    elif 'environment_input_type' in existing_template_schema['schema']:
        template_type = TemplateType.ENVIRONMENT
    else:
        questionary.print('Invalid schema, could not find service_input_type or environment_input_type')
        raise

    # Fill in the main input type references
    if template_type == TemplateType.ENVIRONMENT:
        env_input_ref_value = openapi_spec['components']['schemas']['TemplateInputs']['properties']['spec']['$ref']
        new_template_schema['schema']['environment_input_type'] = __convert_openapi_reference_string_to_template_schema(env_input_ref_value)[2:]

    if template_type == TemplateType.SERVICE_WITHOUT_PIPELINE or template_type == TemplateType.SERVICE:
        service_input_ref_value = openapi_spec['components']['schemas']['ServiceInstanceInputs']['properties']['spec']['$ref']
        new_template_schema['schema']['service_input_type'] = __convert_openapi_reference_string_to_template_schema(service_input_ref_value)[2:]

    if template_type == TemplateType.SERVICE:
        pipeline_input_ref_value = openapi_spec['components']['schemas']['TemplateInputs']['properties']['pipeline']['$ref']
        new_template_schema['schema']['pipeline_input_type'] = __convert_openapi_reference_string_to_template_schema(pipeline_input_ref_value)[2:]

    # Fill in the type definitions
    for type_name, type_def in openapi_spec['components']['schemas'].items():
        if type_name != 'TemplateInputs' and type_name != 'ServiceInstanceInputs':
            __convert_openapi_spec_references_to_template_schema(type_def)
            new_template_schema['schema']['types'][type_name] = type_def

    # Write out the OpenAPI spec to a file
    output_file = os.path.join(template_bundle_dir, 'schema', 'schema.generated.yaml')
    with open(output_file, 'w') as fh_:
        yaml.dump(new_template_schema, fh_)
    questionary.print("Generated Proton template bundle schema file is located at {}".format(output_file))
