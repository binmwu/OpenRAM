#!/usr/bin/env python2.7
"""
Run a regresion test with a wordline_driver array to test delay function
"""

import unittest
from testutils import header
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
import globals
import debug
import calibre
import sys

OPTS = globals.OPTS

#@unittest.skip("SKIPPING 04_driver_test")


class delay_func_test(unittest.TestCase):

    def runTest(self):
        globals.init_openram("config_20_{0}".format(OPTS.tech_name))
        # we will manually run lvs/drc
        OPTS.check_lvsdrc = False

        import wordline_driver
        import tech

        debug.info(2, "Checking driver")
        tx = wordline_driver.wordline_driver(name="Wordline_driver", rows=8)

        self.local_check(tx)
        globals.end_openram()

    def local_check(self, tx):
        delay = tx.delay(slope = 1)
        print "delay",delay


# instantiate a copy of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
