from openvariant.task.count import count

result = count('./data/', './example_2.yaml', where="CHROMOSOME != 12")
print(result)

