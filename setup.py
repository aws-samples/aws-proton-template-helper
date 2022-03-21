import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-proton-helper",
    version="0.1.3",
    author="Aaron Wishnick",
    description="Unofficial helper tool for working with AWS Proton",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/awishn02/aws-proton-helper",
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: Apache Software License",
    ),
    install_requires=[
        'pyyaml',
        'boto3',
        'jinja2',
        'jinja2schema',
        'questionary'
    ],
    scripts=['bin/aws-proton-helper'],
)