<div align="center">
    <br>
    <br>
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

We offer a bunch of [Examples](examples) to we be able to understand how OpenVariant can be applied. Also, check 
[Examples](https://openvariant.readthedocs.io/en/latest/examples.html) section in OpenVariant's documentation.

## Contributing

Feel free to contribute as much as you want to the code.

See [CONTRIBUTING](CONTRIBUTING.md) for guidelines on contributing and respect your behaviour specified
at [CODE OF CONDUCT](CODE_OF_CONDUCT.md).

## License

The software is licensed under [BSD-3-Clause](LICENSE), and the artworks in the images folder are licensed
under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt).