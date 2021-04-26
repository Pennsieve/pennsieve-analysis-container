import os, errno
import csv
import json
from pprint import pprint

def get_csv_files(loc):
    if os.path.isdir(loc):
        for f in os.listdir(loc):
            if not f.startswith('.') and f.endswith('.csv'):
                yield f
    else:
        return None

record_files = get_csv_files('./records/')
relationship_files = get_csv_files('./relationships/')
schema_file = './schema.json'

with open(schema_file, 'r') as f:
    db_schema = json.load(f)


import_args = [" --database=discover.db\n"]

# CREATE THE NODES HEADERS AND ARGS
for f in record_files:
    model_name = f[:-4]
    print(model_name)

    import_args.append('--nodes={}=./records/updated/{}\n'.format(model_name.upper(), f))

    # Get Model Schema for model
    model_schema = list(filter(lambda model: model['name'] == model_name, db_schema['models']))[0]

    # Get first row of the CSV file
    with open('./records/{}'.format(f), 'r') as fp:
        reader = csv.reader(fp)
        headers = next(reader)

    # Create new headers with type info
    new_header = []
    id_defined = False
    for prop in headers:
        prop = prop.replace(':','_')
        print("Property: {}".format(prop))
        if prop == 'id' and not id_defined:
            prop = 'id:ID'
            new_header.append(prop)
            id_defined = True
        elif prop == 'sourcePackageId':
            prop = 'sourcePackageId:string'
            new_header.append(prop)
        else:
            # Get type of prop
            try:
                prop_info = list(filter(lambda p: p['name'] == prop, model_schema['properties']))[0]
                prop_type = prop_info['dataType']['type'].lower()
                if prop_type == "array":
                    elem_type = prop_info['dataType']['items']['type'].lower()
                    if elem_type == 'model':
                        new_header.append('{}:string[]'.format(prop))
                    elif elem_type == 'date':
                         new_header.append('{}:string[]'.format(prop))
                    else:
                        new_header.append('{}:{}[]'.format(prop, elem_type))
                elif prop_type == 'model':
                     new_header.append('{}:string'.format(prop,))
                elif prop_type == 'date':
                    new_header.append('{}:datetime'.format(prop))
                else:
                    new_header.append('{}:{}'.format(prop,prop_info['dataType']['type'].lower()))
            except:
                new_header.append('{}'.format(prop))

    # Create new folder
    try:
        os.makedirs('./records/updated/')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Create new CSV files with updated headers
    with open('./records/{}'.format(f), 'r') as fp:
        reader = csv.DictReader(fp, fieldnames = new_header)
        headers = reader.fieldnames

        # use newline='' to avoid adding new CR at end of line
        with open('./records/updated/{}'.format(f) , 'w', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=reader.fieldnames)
            writer.writeheader()
            header_mapping = next(reader)
            writer.writerows(reader)

# CREATE THE RELATIONSHIPS HEADERS AND ARGS
print("Formatting Relationships")
for f in relationship_files:
    relationship_name = f[:-4]
    print(relationship_name)

    import_args.append('--relationships=./relationships/updated/{}\n'.format(f))

    # Create new folder
    try:
        os.makedirs('./relationships/updated/')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Create new CSV files with updated headers
    new_header = [":START_ID", ":END_ID", ":TYPE"]
    with open('./relationships/{}'.format(f), 'r') as fp:
        reader = csv.DictReader(fp, fieldnames = new_header)
        headers = reader.fieldnames

        # use newline='' to avoid adding new CR at end of line
        with open('./relationships/updated/{}'.format(f) , 'w', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=reader.fieldnames)
            writer.writeheader()
            header_mapping = next(reader)
            writer.writerows(reader)

pprint(import_args)
fo = open("./args.txt", "w")
fo.writelines(import_args)
fo.close()

