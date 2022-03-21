import questionary
from aws_proton_helper.compile.main import guided_compile
from aws_proton_helper.convert_schema.main import convert_template_schema_to_openapi_spec, convert_openapi_spec_to_template_schema

def cli_entry():
    execution_mode = questionary.select(
        "What would you like to do?",
        choices=[
            "Compile",
            "Bundle Template",
            "Validate Template Schema",
            "Convert Template Schema to OpenAPI 3.0 Specification",
            "Convert Generated OpenAPI 3.0 Specification Back to Template Schema"
        ]
    ).ask()

    if (execution_mode == "Compile"):
        guided_compile()
    elif (execution_mode == "Bundle Template"):
        print("Not yet supported")
    elif (execution_mode == "Validate Template Schema"):
        convert_template_schema_to_openapi_spec(outputToFile=False)
    elif (execution_mode == "Convert Template Schema to OpenAPI 3.0 Specification"):
        convert_template_schema_to_openapi_spec()
    elif (execution_mode == "Convert Generated OpenAPI 3.0 Specification Back to Template Schema"):
        convert_openapi_spec_to_template_schema()


def main():
    cli_entry()


if __name__ == "__main__":
    main()