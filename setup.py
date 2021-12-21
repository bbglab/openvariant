from setuptools import setup, find_packages

setup(
    name="open-variant",
    version="0.4.0",
    author="BBGLab - Barcelona Biomedical Genomics Lab",
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests', 'plugins']),
    include_package_data=True,
    install_requires=['pyyaml', 'tqdm', 'click'],
    entry_points={
        'console_scripts': [
            'openvar = openvariant.task.openvar:cli',
        ]
    },
)
