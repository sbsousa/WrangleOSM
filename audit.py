"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = 'sample.osm'

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

# The assignment in the Case Study was to update this variable. Lines 31-52 are my updates.

# UPDATE THIS VARIABLE
mapping = {"St": "Street",
           "St.": "Street",
           "Ave": "Avenue",
           "Ave.": "Avenue",
           "Blvd": "Boulevard",
           "Blvd.": "Boulevard",
           "Dr": "Drive",
           "Dr.": "Drive",
           "Ct": "Court",
           "Ct.": "Court",
           "Pl": "Place",
           "Pl.": "Place",
           "Sq": "Square",
           "Sq.": "Square",
           "Ln": "Lane",
           "Ln.": "Lane",
           "Rd": "Road",
           "Rd.": "Road",
           "Tr": "Trail",
           "Tr.": "Trail",
           "Pkwy": "Parkway",
           "Pkwy.": "Parkway",
           "Cir": "Circle",
           "Cir.": "Circle",
           }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return elem.attrib['k'] == "addr:street"

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


# My code begins here. This is also referenced in data.py
# This function matches the street property in the mapping, splits the abbreviated value, and replaces it with the correct longform value
def update_name(name, mapping):
    match = name.split()
    for i in range(len(match)):
        if match[i] in mapping:
            match[i] = mapping[match[i]]
    name = " ".join(match)
# My code ends here
    return name


def test():
    st_types = audit(OSMFILE)
    assert len(st_types) != 0
    pprint.pprint(dict(st_types))

# Iteritems was modified for Python 3
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
            print(name, "=>", better_name)
            if name == "S Colorado Blvd":
                assert better_name == "S Colorado Boulevard"
            if name == "E Yale Ave":
                assert better_name == "E Yale Avenue"

if __name__ == '__main__':
    test()
