from setuptools import setup, find_packages
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('./requirements.txt', session='hack')

# reqs is a list of requirement
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="he-emulator-client",
    version="0.0.1",
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
    author="Vishal Gowda",
    author_email="vishal@hackerearth.com",
    description="This package contains the Thrift client for "\
        "emulator endpoints",
)
