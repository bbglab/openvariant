<div align="center">
    <a href="https://openvariant.readthedocs.io/">
      <img src="https://github.com/bbglab/openvariant/raw/master/logo.png" width="590" height="350">
    </a>
    <br>
    <br>
  	<a href="https://opensource.org/licenses/BSD-3-Clause">
  		<img alt="License" src="https://img.shields.io/github/license/bbglab/openvariant">
  	</a>
  	<a href="https://pypi.org/project/open-variant/">
  		<img alt="PyPi" src="https://img.shields.io/pypi/v/open-variant">
  	</a>
     <a href="https://github.com/bbglab/openvariant/actions/workflows/openvariant_tester.yml">
         <img alt="Test" src="https://github.com/bbglab/openvariant/actions/workflows/openvariant_tester.yml/badge.svg">
     </a>
    <a href="https://codecov.io/gh/bbglab/openvariant" > 
        <img alt="Coverage" src="https://codecov.io/gh/bbglab/openvariant/branch/develop/graph/badge.svg?token=N6HUMWS9U5"/> 
    </a>
  	<a href="https://openvariant.readthedocs.io/en/latest/?badge=latest">
  		<img alt="Documentation Status" src="https://readthedocs.org/projects/openvariant/badge/?version=latest">
  	</a>
    <br>
    <br>
</div>

OpenVariant is a comprehensive Python package that provides different functionalities to read, parse and operate
different multiple input file formats (e. g. ``tsv``, ``csv``, ``vcf``, ``maf``, ``bed``), being able to customize the output.

Its aim is being able to manage a ton of data represented in multiple ways and be able to build an unified output with 
a proper annotation file structure. This package was thought to work with any kind of data that can be represented 
as a table.

_Documentation_: [https://openvariant.readthedocs.io](https://openvariant.readthedocs.io)

## Features

OpenVariant offers a toolkit to transform and operate the parsed input data. We will be able to apply different 
functionalities on our parsed result some of them are the following ones:

- Find files
- Read and save
- Cat
- Group by
- Count
- Command-line interface (CLI)
- Plugins

<div align="center">
  <a href="https://openvariant.readthedocs.io/en/latest/user_guide.html">
    <img src="https://github.com/bbglab/openvariant/raw/master/workflow.gif" width="600" height="352">
  </a>
</div>

Check [User guide](https://openvariant.readthedocs.io/en/latest/user_guide.html) in OpenVariant's documentation to find all the information about how it works 
and how can be applied the different functionalities.  

## Installation

It requires Python 3 or higher and can be installed as [PyPI package](https://pypi.org/project/open-variant/) with:

```bash
pip install open-variant
```

For more details check our [Installation](https://openvariant.readthedocs.io/en/latest/installation.html) section.

## Examples

We provide a variety of [examples](https://github.com/bbglab/openvariant/tree/master/examples) to help to understand how OpenVariant can be applied. Explore the 
[Examples](https://openvariant.readthedocs.io/en/latest/examples.html) section in OpenVariant's documentation for more details.

As well, we present a small dataset for hands-on use with OpenVariant, allowing users to test the tool's functionalities. It may be found at [Zenodo](https://zenodo.org/records/14215914) and it can be downloaded using the following commands:
```bash
pip install zenodo_get                      
zenodo_get 14215914
```

## Contributing

You're welcome to contribute to the code as much as you'd like!

Please review the guidelines outlined in the [Contributing](https://github.com/bbglab/openvariant/blob/master/CONTRIBUTING.md) document and adhere to the standards of conduct detailed in the [Code of Conduct](https://github.com/bbglab/openvariant/blob/master/CODE_OF_CONDUCT.md).

## License

The software is licensed under [BSD-3-Clause](https://github.com/bbglab/openvariant/blob/master/LICENSE).

## Reference

If you use OpenVariant in your research, please cite:

> David Martínez-Millán, Federica Brando, Miguel L. Grau, Mònica Sánchez-Guixé, Carlos López-Elorduy, Iker Reyes-Salazar, Jordi Deu-Pons, Núria López-Bigas, Abel González-Pérez, OpenVariant: a toolkit to parse and operate multiple input file formats, Bioinformatics, Volume 40, Issue 12, December 2024, btae714, [https://doi.org/10.1093/bioinformatics/btae714](https://doi.org/10.1093/bioinformatics/btae714)
