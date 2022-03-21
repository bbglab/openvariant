from setuptools import setup, find_packages

setup(
    name="open-variant",
    version="0.6.13",
    author="BBGLab - Barcelona Biomedical Genomics Lab",
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    install_requires=['pyyaml', 'tqdm', 'click'],
    entry_points={
        'console_scripts': [
            'openvar = openvariant.commands.openvar:openvar',
        ]
    },
)
