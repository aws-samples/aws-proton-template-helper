import questionary

def prompt_for_environment_name(proton_client):
    environment_name = questionary.text("What Environment would you like to retrieve the Spec from? If you're not sure, enter nothing and I will list the environments in your account").ask()

    if environment_name == "":
        environment_options = []
        for environment in proton_client.list_environments()['environments']:
            environment_options.append(environment['name'])
        environment_name = questionary.select("Which environment?", choices=environment_options).ask()
    
    return environment_name

def prompt_for_service_name(proton_client):
    service_name = questionary.text("What Service would you like to retrieve the Spec from? If you're not sure, enter nothing and I will list the services in your account").ask()

    if service_name == "":
        service_options = []
        for service in proton_client.list_services()['services']:
            service_options.append(service['name'])
        service_name = questionary.select("Which service?", choices=service_options).ask()
    
    return service_name