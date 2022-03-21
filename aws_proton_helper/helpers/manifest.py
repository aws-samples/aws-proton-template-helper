import yaml
import questionary
import os

def get_cfn_file_path(directory):
    with open(os.path.join(directory, "manifest.yaml"), 'r') as fh_:
        manifest_yaml = yaml.safe_load(fh_.read())

    if (len(manifest_yaml["infrastructure"]["templates"]) != 1 or
       manifest_yaml["infrastructure"]["templates"][0]["rendering_engine"] != "jinja" or
       manifest_yaml["infrastructure"]["templates"][0]["template_language"] != "cloudformation"):
        questionary.print("I only support single file / cloudformation / jinja templates right now")
        raise

    return os.path.join(directory, manifest_yaml["infrastructure"]["templates"][0]["file"])