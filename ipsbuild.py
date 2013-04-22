#!/usr/bin/env python
# This file is part of ipsutils.

# ipsutils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ipsutils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ipsutils.  If not, see <http://www.gnu.org/licenses/>.


from pprint import pprint
import ips

testfile = "test.ips"
build = ips.build.Build(testfile)
build.show_summary()
build.controller.do_tasks()
