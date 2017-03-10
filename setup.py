from setuptools import setup, find_packages

setup(
    name="he-emulator-client",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "thrift>=0.9.3",
    ],
    include_package_data=True,
    author="Vishal Gowda",
    author_email="vishal@hackerearth.com",
    description="This package contains the Thrift client for "\
        "emulator endpoints",
)
