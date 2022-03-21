import questionary
from aws_proton_helper.compile.main import guided_compile

def cli_entry():
    execution_mode = questionary.select(
        "What would you like to do?",
        choices=["Compile", "Bundle Template"]
    ).ask()

    if (execution_mode == "Compile"):
        guided_compile()
    elif (execution_mode == "Bundle Template"):
        print("Not yet supported")


def main():
    cli_entry()


if __name__ == "__main__":
    main()