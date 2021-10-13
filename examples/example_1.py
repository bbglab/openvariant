from openvariant.annotation.annotation import Annotation
from openvariant.variant.variant import Variant

annotation = Annotation('./example_1.yaml')

result = Variant('./data/', annotation)
print(' '.join(result.header))
for r in result.read():
    print(r['by_OpenVariant'], r['CHROMOSOME'], r['DATASET'], r['PROJECT'])


