from setuptools import setup, find_packages

# Read long description from README.rst
with open("README.rst", "r") as f:
    long_description = f.read()

requirements = [
    "apache-airflow[ssh]>=1.10",
    "fabric>=2.5"
]

requirements_docs = [
    "sphinx>=3.5",
    "sphinx-rtd-theme",
    "sphinx-autodoc-typehints",
    "sphinx-versions"
]

requirements_tests = [
    "pytest",
    "faker"
]

setup(
    name="sai-airflow-plugins",
    version="0.1.0",
    author="Slimmer.AI",
    description="A Python package with various operators, hooks and utilities for Apache Airflow",
    long_description=long_description,
    url="https://github.com/Slimmer-AI/sai-airflow-plugins",
    license="Apache License 2.0",
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

        # Intended audiences
        "Intended Audience:: Developers",
        "Intended Audience :: System Administrators",

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
