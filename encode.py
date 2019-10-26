#!/usr/bin/env python2
# -*- coding: latin-1 -*-
'''GET an object from an ENCODE server'''

import requests

# Supported file formats

FORMATS = set(["bigBed", "bigWig", "bedpe", "tsv"])
#FORMATS = set(["bigBed", "bigWig", "bedpe", "tsv", "hic"])

# Force return from the server in JSON format
HEADERS = {'accept': 'application/json'}

URL = "https://www.encodeproject.org/search/?" \
      "type=Experiment&" \
      "format=json&" \
      "field=biosample_summary&" \
      "field=lab.title&" \
      "field=biosample_ontology.name&" \
      "field=assay_term_name&" \
      "field=target.title&" \
      "field=files.file_format&" \
      "field=files.output_type&" \
      "field=files.href&" \
      "field=files.technical_replicates&" \
      "field=files.biological_replicates&" \
      "field=files.assembly&" \
      "field=files.accession&" \
      "limit=all"

# GET the object
response = requests.get(URL, headers=HEADERS)

# Extract the JSON response as a python dict
response_json_dict = response.json()

# Graph object
graph = response_json_dict['@graph']

# Dicitionary for results

results = {}


def listToString(l):
    result = ''
    for i in range(len(l)):
        if i > 0:
            result += ","
        result += str(l[i])
    return result


for record in graph:

    id = record["@id"]
    experiment = id[13:][:-1]
    if 'biosample_summary' in record:
        biosample = record['biosample_summary']
    else:
        biosample = ''
    assay_type = record['assay_term_name']
    lab = record['lab']['title']
    if 'target' in record:
        target = record['target']['title'].replace('(Homo sapiens)', '')
    else:
        target = ''

    # print(cell_type + '\t' + assay_type + '\t' + target)
    if 'files' in record:
        for file in record['files']:
            if 'assembly' in file and 'href' in file:

                assembly = file['assembly']
                format = file['file_format']
                output_type = file['output_type']
                accession = file['accession']

                if format == 'tsv':
                    if assay_type.lower() != 'hic':
                        continue;

                bio_rep = ''
                tech_rep = ''
                if 'biological_replicates' in file:
                    bio_rep = listToString(file['biological_replicates'])

                if 'technical_replicates' in file:
                    tech_rep = listToString(file['technical_replicates'])

                if assembly in results:
                    r = results[assembly]
                else:
                    r = []
                    results[assembly] = r

                if format in FORMATS:
                    r.append(id + '\t' + assembly + '\t' + biosample + '\t' + assay_type + '\t' + target + '\t' +
                             str(bio_rep) + '\t' + str(tech_rep) + '\t' + output_type + '\t' + format + '\t' +
                             lab + '\t' + file['href'] + '\t' + accession + '\t' + experiment)

for a in list(results):

    fname = 'output/' + a + ".txt"

    with open(fname, 'w') as f:

        print(
            'ID\tAssembly\tBiosample\tAssayType\tTarget\tBioRep\tTechRep\tOutputType\tFormat\tLab\tHREF\tAccession\tExperiment',
            file=f)

        r = results[a]

        for x in r:
            print(x, file=f)
