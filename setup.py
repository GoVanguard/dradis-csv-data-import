import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csv2dradis",
    version="0.2.0",
    author="Shane Scott",
    author_email="sscott@govanguard.com",
    description="Optimization of csvtodradis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GoVanguard/csv2dradis",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: GPLv2 License",
        "Operating System :: OS Independent",
    ),
)
