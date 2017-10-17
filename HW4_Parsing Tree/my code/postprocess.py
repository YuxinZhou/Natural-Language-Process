#!/usr/bin/env python

import sys, fileinput
import tree

#!/usr/bin/env python

import sys, fileinput
import tree
# f = open('dev.parsing.post', 'w')

for line in fileinput.input():
    # if line != '\n':

    t = tree.Tree.from_str(line)
    if t.root is None:
        print
        continue
    t.restore_unit()
    t.unbinarize()

    print t


