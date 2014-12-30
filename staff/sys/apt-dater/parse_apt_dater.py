#!/usr/bin/env python
# encoding: utf8

import sys
from collections import defaultdict
from lxml import etree

t = etree.parse(sys.stdin)
# print etree.tostring(t)
# print t

updates = t.xpath("//pkg[@hasupdate='1']")
# print updates

collected = defaultdict(list)

for u in updates:
    collected[u.xpath("../..")[0].attrib["hostname"]].append(
        "{name}: {old} --> {new}".format(name = u.attrib["name"], old = u.attrib["version"], new = u.attrib.get("data")))

for host in sorted(collected.keys()):
    print host
    updates = collected[host]
    print "\t", "\n\t".join(updates)
