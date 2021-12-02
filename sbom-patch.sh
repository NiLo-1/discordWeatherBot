#!/usr/bin/env bash
AUTHOR_NAME="Nile Kelly"
AUTHOR_EMAIL="nilekell@gmail.com"
TOOL_NAME="sbom-patch"
TOOL_VERSION="unknown"
FORMAT=cyclonedx
COMPONENT_AUTHOR_NAME="$AUTHOR_NAME"
SUPPLIER_NAME="$AUTHOR_NAME"
SUPPLIER_URL=https://github.com/nilekell/discordWeatherBot
TOOL_VENDOR="$AUTHOR_NAME"
TOOL_HASH_ALG="SHA-256"
# shellcheck disable=SC2002
TOOL_HASH_CONTENT=$(shasum -a 256 "$0" | cut -d' ' -f1)
# credentials directory should have 0700 permissions
PRIVACY=PUBLIC
OUTPUT=sbom.orig.xml
PATCHED_OUTPUT=sbom.xml
python3 <(cat <<END
import sys
import xml.etree.ElementTree as ET
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
ET.register_namespace('', 'http://cyclonedx.org/schema/bom/1.2')
ns = {'': 'http://cyclonedx.org/schema/bom/1.2'}
# Open original file
print(sys.stdin.read())
et = ET.parse(sys.stdin)
root = et.getroot()
metadata = root.find('metadata', ns)
# Add this tool
tools = metadata.find('tools', ns)
if not tools:
    tools = ET.SubElement(metadata, 'tools')
tool = ET.SubElement(tools, 'tool')
ET.SubElement(tool, 'vendor').text = '$TOOL_VENDOR'
ET.SubElement(tool, 'name').text = '$TOOL_NAME'
ET.SubElement(tool, 'version').text = '$TOOL_VERSION'
hashes = ET.SubElement(tool, 'hashes')
hash = ET.SubElement(hashes, 'hash', alg='${TOOL_HASH_ALG}')
hash.text = '$TOOL_HASH_CONTENT'
# Add sbom authors elements
authors = metadata.find('authors', ns)
if not authors:
    authors = ET.Element('authors')
    metadata.insert(2, authors)
author = ET.SubElement(authors, 'author')
ET.SubElement(author, 'name').text = '$AUTHOR_NAME'
ET.SubElement(author, 'email').text = '$AUTHOR_EMAIL'
component = metadata.find('component', ns)
# Update component publisher and author
publisher = component.find('publisher', ns)
if not publisher:
    publisher = ET.Element('publisher')
    component.insert(0, publisher)
publisher.text = '$COMPONENT_AUTHOR_NAME'
author = component.find('author', ns)
if not author:
    author = ET.Element('author')
    component.insert(0, author)
author.text = '$COMPONENT_AUTHOR_NAME'
# Update component name and version
component.find('name', ns).text = '$COMPONENT_NAME'
component.find('version', ns).text = '$COMPONENT_VERSION'
# Update component hash
hashes = component.find('hashes', ns)
if not hashes:
    hashes = ET.SubElement(component, 'hashes')
hash = ET.SubElement(hashes, 'hash', alg='${COMPONENT_HASH_ALG}')
hash.text = '$COMPONENT_HASH_CONTENT'
# Add component supplier
supplier = component.find('supplier', ns)
if not supplier:
    supplier = ET.Element('supplier')
    component.insert(0, supplier)
ET.SubElement(supplier, 'name').text = '$SUPPLIER_NAME'
ET.SubElement(supplier, 'url').text = '$SUPPLIER_URL'
# Add supplier (it appears twice in the schema)
supplier = metadata.find('supplier', ns)
if not supplier:
    supplier = ET.SubElement(metadata, 'supplier')
ET.SubElement(supplier, 'name').text = '$SUPPLIER_NAME'
ET.SubElement(supplier, 'url').text = '$SUPPLIER_URL'
indent(root)
et.write(sys.stdout, encoding='unicode', xml_declaration=True, default_namespace='')
END
) < "$OUTPUT" > "$PATCHED_OUTPUT"
