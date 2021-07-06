from setuptools import setup, find_packages

# Read long description from README.rst
with open("README.rst", "r") as f:
    long_description = f.read()

# Read version number from VERSION
with open("VERSION", "r") as f:
    version = f.read()

requirements = [
    "apache-airflow[ssh]>=1.10",
    "fabric>=2.5"
]

requirements_docs = [
    "sphinx>=3.5,<4",
    "sphinx-rtd-theme",
    "sphinx-autodoc-typehints",
    "sphinx-versions==1.0.1"
]

requirements_tests = [
    "pytest",
    "faker"
]

setup(
    name="sai-airflow-plugins",
    version=version,
    author="Slimmer.AI",
    description="A Python package with various operators, hooks and utilities for Apache Airflow",
    long_description=long_description,
    url="https://github.com/Slimmer-AI/sai-airflow-plugins",
    license="Apache License 2.0",
    license_files=["LICENSE"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={"docs": requirements_docs,
                    'tests': requirements_tests},
    test_suite="tests",
    tests_require=requirements_tests,
    classifiers=[
        # Development status
        "Development Status :: 5 - Production/Stable",

        # Environments
        "Environment :: Plugins",

        # Supported Python versions
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        # License
        "License :: OSI Approved :: Apache Software License",

        # Topic
        "Topic :: System :: Monitoring"
    ]
)
