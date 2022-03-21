from jinja2 import Environment, Template
from jinja2schema import infer_from_ast, model
import questionary

def get_all_variables(template_text):
    env = Environment()
    ast = env.parse(template_text)
    return infer_from_ast(ast)


def get_raw_inputs(all_variables, prefix=""):
    inputs = {}
    for key, value in all_variables.items():
        cur_var = key
        if prefix != "":
            cur_var = prefix + "." + cur_var
        if type(value) is model.Dictionary:
            inputs[key] = get_raw_inputs(value, cur_var)
        elif type(value) is model.Scalar:
            inputs[key] = questionary.text("Enter value for " + cur_var).ask()
        else:
            print("Unexpected variable type, unable to infer schema: " + type(value))
            raise 
    return inputs


def render_jinja(jinja_text, inputs):
    jinja_template = Template(jinja_text)
    return jinja_template.render(inputs)