from openvariant.annotation.annotation import Annotation
from openvariant.variant.variant import Variant

annotation = Annotation('./tests/data/example.yaml')
result = Variant('./tests', annotation)
for r in result.read():
    print(r)
print(result)
