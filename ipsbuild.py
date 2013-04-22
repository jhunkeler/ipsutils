#!/usr/bin/env python

# Solaris 11 IPS
# Automate package creation

from pprint import pprint
import ips

testfile = "test.ips"
build = ips.build.Build(testfile)
#build.show_summary()
#build.source_unpack()
build.controller.do_tasks()
print("I made it to the end")