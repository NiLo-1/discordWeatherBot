#!/usr/bin/env python3

import os, sys
import xml.etree.ElementTree as ET
import hashlib

CYCLONEDX_BOM_NS='http://cyclonedx.org/schema/bom/1.2'

AUTHOR_NAME="Nile Kelly"
AUTHOR_EMAIL="nilekell@gmail.com"
TOOL_NAME="sbom-patch"
TOOL_VERSION="unknown"
FORMAT="cyclonedx"
COMPONENT_NAME="discordWeatherBot"
COMPONENT_VERSION=f"0.0.{os.environ.get('GITHUB_RUN_ID', '1')}"
COMPONENT_AUTHOR_NAME=AUTHOR_NAME
SUPPLIER_NAME=AUTHOR_NAME
SUPPLIER_URL="https://github.com/nilekell/discordWeatherBot"
TOOL_VENDOR=AUTHOR_NAME
TOOL_HASH_ALG="SHA-256"
COMPONENT_HASH_ALG="SHA-256"

def hash256file(filename):
    with open(filename,"rb") as f:
        bytes = f.read() # read entire file as bytes
        digest = hashlib.sha256(bytes).hexdigest()
        return digest

TOOL_HASH_CONTENT=hash256file(__file__)
COMPONENT_HASH_CONTENT=os.environ.get(
    "GITHUB_SHA", hash256file("weatherbot.py"))

PRIVACY="PUBLIC"
OUTPUT="sbom.orig.xml"

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

ET.register_namespace('', CYCLONEDX_BOM_NS)
ns = {'': CYCLONEDX_BOM_NS}

# Open original file
et = ET.parse(OUTPUT)
root = et.getroot()
metadata = root.find('metadata', ns)

# Add this tool
tools = metadata.find('tools', ns)
if not tools:
    tools = ET.SubElement(metadata, 'tools')
tool = ET.SubElement(tools, 'tool')
ET.SubElement(tool, 'vendor').text = TOOL_VENDOR
ET.SubElement(tool, 'name').text = TOOL_NAME
ET.SubElement(tool, 'version').text = TOOL_VERSION
hashes = ET.SubElement(tool, 'hashes')
hash = ET.SubElement(hashes, 'hash', alg=TOOL_HASH_ALG)
hash.text = TOOL_HASH_CONTENT
# Add sbom authors elements
authors = metadata.find('authors', ns)
if not authors:
    authors = ET.Element('authors')
    metadata.insert(2, authors)
author = ET.SubElement(authors, 'author')
ET.SubElement(author, 'name').text = AUTHOR_NAME
ET.SubElement(author, 'email').text = AUTHOR_EMAIL

# credentials directory should have 0700 permissions
component = metadata.find('component', ns)

if component is None:
    component = ET.SubElement(metadata, 'component')

# Update component publisher and author
publisher = component.find('publisher', ns)
if not publisher:
    publisher = ET.Element('publisher')
    component.insert(0, publisher)
publisher.text = COMPONENT_AUTHOR_NAME
author = component.find('author', ns)
if not author:
    author = ET.Element('author')
    component.insert(0, author)
author.text = COMPONENT_AUTHOR_NAME
# Update component name and version


def find_or_add(e, child, **attrs):
    sub = e.find('name', ns)
    if sub is not None:
        return sub
    return ET.SubElement(e, child, **attrs)


def find_or_insert(e, child, **attrs):
    sub = e.find('name', ns)
    if sub is not None:
        return sub

    supplier = ET.Element('supplier')
    e.insert(0, supplier)
    return supplier


find_or_add(component, 'name').text = COMPONENT_NAME
find_or_add(component, 'version').text = COMPONENT_VERSION
# Update component hash
hashes = find_or_add(component, 'hashes')
hash = ET.SubElement(hashes, 'hash', alg=COMPONENT_HASH_ALG)
hash.text = COMPONENT_HASH_CONTENT
# Add component supplier
supplier = find_or_insert(component, 'supplier')
ET.SubElement(supplier, 'name').text = SUPPLIER_NAME
ET.SubElement(supplier, 'url').text = SUPPLIER_URL
# Add supplier (it appears twice in the schema)
supplier = find_or_add(metadata, 'supplier')
find_or_add(supplier, 'name').text = SUPPLIER_NAME
find_or_add(supplier, 'url').text = SUPPLIER_URL
indent(root)

et.write(sys.stdout, encoding='unicode', xml_declaration=True, default_namespace='')
