from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="open-variant",
    version="1.0.0",
    author="BBGLab - Barcelona Biomedical Genomics Lab",
    author_email='bbglab@irbbarcelona.org',
    description="OpenVariant provides different functionalities to read, parse and operate different multiple input "
                "file formats, being able to customize the output.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD 3-Clause License',
    keywords='bioinformatics,openvariant,openvar,bbglab',
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    install_requires=['pyyaml', 'tqdm', 'click', 'pyliftover', 'appdirs'],
    entry_points={
        'console_scripts': [
            'openvar = openvariant.commands.openvar:openvar',
        ]
    },
    url="https://github.com/bbglab/openvariant",
)
