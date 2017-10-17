# Sep 30, 2017
# Yuxin Zhou
from collections import defaultdict
import tree
import re
import os, fileinput
import math
import time
import argparse
import sys
import codecs

if sys.version_info[0] == 2:
    from itertools import izip
else:
    izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit


scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')


def prepfile(fh, code):
    if type(fh) is str:
        fh = open(fh, code)
    ret = gzip.open(fh.name, code if code.endswith("t") else code + "t") if fh.name.endswith(".gz") else fh
    if sys.version_info[0] == 2:
        if code.startswith('r'):
            ret = reader(fh)
        elif code.startswith('w'):
            ret = writer(fh)
        else:
            sys.stderr.write("I didn't understand code " + code + "\n")
            sys.exit(1)
    return ret


def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
    ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
    group = parser.add_mutually_exclusive_group()
    dest = arg if dest is None else dest
    group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
    group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)


# the parameter of defaultdict must be a constructor
# leftdict = {left: {right: count, right2: count2, ...}, left: {...}, ...}

leftdict = defaultdict(lambda: defaultdict(int))
rightdict = defaultdict(lambda: defaultdict(int))
xdata = []
ydata = []


def prepfile(fh, code):
    if type(fh) is str:
        fh = open(fh, code)
    ret = gzip.open(fh.name, code if code.endswith("t") else code + "t") if fh.name.endswith(".gz") else fh
    if sys.version_info[0] == 2:
        if code.startswith('r'):
            ret = reader(fh)
        elif code.startswith('w'):
            ret = writer(fh)
        else:
            sys.stderr.write("I didn't understand code " + code + "\n")
            sys.exit(1)
    return ret




def learning_rules(line):
    t = tree.Tree.from_str(line)
    nodes = t.bottomup()
    for n in nodes:
        if len(n.children) == 2:
            leftdict[n.label][n.children[0].label + ' ' + n.children[1].label] += 1
        elif len(n.children) == 1:
            leftdict[n.label][n.children[0].label.lower()] += 1
    return


def calculate_prob(dct):
    r = []
    for parent in dct:
        count = 0
        for child in dct[parent]:
            count += dct[parent][child]

        # Smooth
        if dct[parent]['<unk>'] == 0:
            count += 1
            dct[parent]['<unk>'] = 1

        for child in dct[parent]:
            prob = dct[parent][child] / float(count)
            r.append("{0} -> {1} # {2}".format(parent, child, prob))
            rightdict[child][parent] = prob
    return r


def parsing_tree(text):
    text_org = text.strip().split(' ')
    text = text.strip().lower()
    text = text.split(' ')
    tlen = len(text)
    # Each DP cell: dict{left: prob, ...}
    dp = [[defaultdict(lambda: float('-inf')) for _ in range(tlen)] for _ in range(tlen)]
    # Each backpoint cell: tuple(breakpoint, 'left -> right')
    backpoints = [[defaultdict(lambda: None) for _ in range(tlen)] for _ in range(tlen)]
    # Viterbi CKY
    for delta in range(0, tlen):
        for row in range(tlen):
            col = row + delta
            if col >= tlen:
                break
            cell = dp[row][col]
            if delta == 0:
                for left in rightdict[text[row]]:
                    right = text[row]
                    cell[left] = math.log10(rightdict[right][left])
                    rule = left + ' -> ' + text_org[row]
                    backpoints[row][col][left] = (None, rule)
                if not rightdict[text[row]]:
                    for left in rightdict['<unk>']:
                        right = text[row]
                        cell[left] = math.log10(rightdict['<unk>'][left])
                        rule = left + ' -> ' + text_org[row]
                        backpoints[row][col][left] = (None, rule)
            else:
                for breakpoint in range(0, delta):
                    c1 = dp[row][breakpoint + row]
                    c2 = dp[breakpoint + row + 1][col]
                    for left1, prob1 in c1.iteritems():
                        for left2, prob2 in c2.iteritems():
                            right = left1 + ' ' + left2
                            for left in rightdict[right]:
                                prob = math.log10(rightdict[right][left])
                                prob += prob1
                                prob += prob2
                                if prob > cell[left]:
                                    cell[left] = prob
                                    rule = left + ' -> ' + right
                                    backpoints[row][col][left] = (breakpoint, rule)

    # construct a tree
    stack = []
    row, col = 0, tlen - 1
    root = None
    # # Guessing
    # if backpoints[row][col]['TOP'] is None:
    #     cell = dp[row][col]
    #     for breakpoint in range(0, tlen - 1):
    #         c1 = dp[row][breakpoint + row]
    #         c2 = dp[breakpoint + row + 1][col]
    #         for left1, prob1 in c1.iteritems():
    #             for left2, prob2 in c2.iteritems():
    #                 right = left1 + ' ' + left2
    #                 prob = prob1 + prob2
    #                 if prob > cell['TOP']:
    #                     cell['TOP'] = prob
    #                     rule = 'TOP' + ' -> ' + right
    #                     backpoints[row][col]['TOP'] = (breakpoint, rule)

    if backpoints[row][col]['TOP'] is not None:
        root = tree.Node('TOP', [])
        stack.append((root, row, col))

    while stack:
        node, row, col = stack.pop()
        breakpoint, backrule = backpoints[row][col][node.label]
        parent, children = re.split(' -> ', backrule)
        children = children.split(' ')
        if len(children) == 1:
            assert row == col
            node.append_child(tree.Node(children[0], []))
        else:
            assert breakpoint is not None
            lchild = tree.Node(children[0], [])
            rchild = tree.Node(children[1], [])
            node.append_child(lchild)
            node.append_child(rchild)
            stack.append((lchild, row, row + breakpoint))
            stack.append((rchild, row + breakpoint + 1, col))
    if root:
        t = tree.Tree(root)
        return t
    else:
        return None


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="add header, line numbers",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addonoffarg(parser, 'debug', help="debug mode", default=False)
    parser.add_argument("--train", "-t", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="train file")
    parser.add_argument("--inputfile", "-d", nargs='?', type=argparse.FileType('r'), default=sys.stdout,
                        help="input file")
    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    workdir = tempfile.mkdtemp(prefix=os.path.basename(__file__), dir=os.getenv('TMPDIR', '/tmp'))



    def cleanwork():
        shutil.rmtree(workdir, ignore_errors=True)


    if args.debug:
        print(workdir)
    else:
        atexit.register(cleanwork)

    trainfile = prepfile(args.train, 'r')
    inputfile = prepfile(args.inputfile, 'r')

    for ln, line in enumerate(trainfile, start=1):
        learning_rules(line)


    rules = calculate_prob(leftdict)

    for text in inputfile:
        parsed_tree = parsing_tree(text)
        if parsed_tree:
            print parsed_tree
        else:
            print
