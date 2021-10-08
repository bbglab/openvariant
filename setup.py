from setuptools import setup, find_packages

setup(
    name="open-variant",
    version="0.0.2",
    author="BBGLab - Barcelona Biomedical Genomics Lab",
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests', 'plugins']),
    include_package_data=True,
    install_requires=['pyyaml'],
)
