# Examples to run

In order to be able to run the different examples, you need to install __OpenVariant__ with PyPi. 
Also, it is recommended to use your favourite Python environment to avoid any kind of versioning problem.  

```bash
pip install open-variant
```

You can check out `example_1.py` and `example_2.py` to figure out how __OpenVariant__ can be used.

### Command line examples:

```bash
openvar cat ./data -a example_2.yaml | head
```
```bash
openvar groupby ./data -a example_2.yaml -g CHROMOSOME -q
```
```bash
openvar count ./data -a example_2.yaml -w "CHROMOSOME != 12"
```
