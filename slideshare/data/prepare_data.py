import json

infile = open('institutions.txt')
outfile = open('institutions.json', 'w')

augmented = []
for line in infile.readlines():
    if len(line) > 60 or len(line.split(',')) > 2:
        print(line)
        continue
    inst,state = line.split(",")
    augmented.append({ "value": inst, "label": line[:-1] })

outfile.write(json.dumps(augmented))
