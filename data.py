import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "sample.osm"

# Street name array and conversion mapping from audit.py
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

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

# Udacity variables provided in original data.py sample
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=+/&<>;\'"?%#$@,. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        # iterate over node attributes
        for i in node_attr_fields:
            if i in NODE_FIELDS:
                node_attribs[i] = element.attrib[i]
        # iterate over node_tags
        for node_tag in element:
            tag = {}
            # if the tag "k" attribute contains problematic characters, stop processing. Continue to the next condition in the loop.
            if problem_chars.search(node_tag.attrib['k']):
                continue
            # find each matching tag attribute, split into colon-separated list, and index at the specified position
            elif LOWER_COLON.search(node_tag.attrib['k']):
                tag['id'] = element.attrib['id']
                tag['key'] = node_tag.attrib['k'].split(':', 1)[1]
                tag['value'] = node_tag.attrib['v']
                tag['type'] = node_tag.attrib['k'].split(':', 1)[0]
                tags.append(tag)
            # iterate over street names using audit.py method
            elif node_tag.attrib['k'] == 'addr:street' and node_tag.attrib['k'] != '':
                tag['value'] = update_name(str(node_tag.attrib['v']).replace("`", "").strip(), mapping)
                tag['type'] = node_tag.attrib['k'].split(':', 1)[0]
                tags.append(tag)
            # clean the name tags that include street addresses
            elif node_tag.attrib['k'] == 'name' and node_tag.attrib['k'] != '':
                tag['id'] = element.attrib['id']
                tag['key'] = node_tag.attrib['k']
                tag['value'] = update_name(str(node_tag.attrib['v']).replace("`", "").strip(), mapping)
                tag['type'] = node_tag.attrib['k'].split(':', 1)[0]
                tags.append(tag)
            # If a node has no secondary tags then the "node_tags" field should just contain an empty list.
            else:
                tag['id'] = element.attrib['id']
                tag['key'] = node_tag.attrib['k']
                tag['value'] = node_tag.attrib['v']
                tag['type'] = default_tag_type
                tags.append(tag)

        # print statement can be uncommented to monitor output for sample.osm
        # print({'node': node_attribs, 'node_tags': tags})

        # return all cleaned and unchanged nodes and node_tags
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for j in way_attr_fields:
            if j in WAY_FIELDS:
                way_attribs[j] = element.attrib[j]
        # variable to set a counter for the way tag position
        n: int = 0
        for way_tag in element:
            tag = {}
            node = {}
            if way_tag.tag == 'tag':
                if problem_chars.search(way_tag.attrib['k']):
                    continue
                elif LOWER_COLON.search(way_tag.attrib['k']):
                    tag['id'] = element.attrib['id']
                    tag['key'] = way_tag.attrib['k'].split(':', 1)[1]
                    tag['value'] = way_tag.attrib['v']
                    tag['type'] = way_tag.attrib['k'].split(':', 1)[0]
                    tags.append(tag)
                elif way_tag.attrib["k"] == 'addr:street' and way_tag.attrib["k"] != '':
                    tag['value'] = update_name(str(way_tag.attrib['v']).replace("`", "").strip(), mapping)
                    tag["type"] = way_tag.attrib['k'].split(":", 1)[0]
                elif way_tag.attrib['k'] == 'name' and way_tag.attrib['k'] != '':
                    tag['id'] = element.attrib['id']
                    tag['key'] = way_tag.attrib['k']
                    tag['value'] = update_name(str(way_tag.attrib['v']).replace("`", "").strip(), mapping)
                    tag["type"] = way_tag.attrib['k'].split(":", 1)[0]
                    tags.append(tag)
                else:
                    tag['id'] = element.attrib['id']
                    tag['key'] = way_tag.attrib['k']
                    tag['value'] = way_tag.attrib['v']
                    tag['type'] = default_tag_type
                    tags.append(tag)
            elif way_tag.tag == 'nd':
                node['id'] = element.attrib['id']
                node['node_id'] = way_tag.attrib['ref']
                node['position'] = n
                # in-place operator to add 1 to the index and retain the way node position order
                n += 1
                way_nodes.append(node)
        # print statement can be uncommented to monitor output for sample.osm
        # print({'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags})
        # return all ways, way_nodes, and way_tags
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def update_name(name, mapping):
    match = name.split()
    for i in range(len(match)):
        if match[i] in mapping:
            match[i] = mapping[match[i]]
    name = " ".join(match)
    # My code ends here
    return name


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(iter(validator.errors.items()))
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: v for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', "utf-8") as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w', "utf-8") as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w', "utf-8") as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w', "utf-8") as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w', "utf-8") as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=True)
