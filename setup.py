from setuptools import setup, find_packages

setup(
    name="open-variant",
    version="0.4.7",
    author="BBGLab - Barcelona Biomedical Genomics Lab",
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    include_package_data=True,
    install_requires=['pyyaml', 'tqdm', 'click'],
    entry_points={
        'console_scripts': [
            'openvar = openvariant.commands.openvar:main',
        ]
    },
)
