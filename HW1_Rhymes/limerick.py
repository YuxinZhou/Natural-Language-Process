#!/usr/bin/env python
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

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')
prondict = nltk.corpus.cmudict.dict()


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


class LimerickDetector:
    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()

    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.

        The number of sounds in the pronunciation dictionary lookup that
        end in a digit = the number of syllables.
        """
        prons = prondict.get(word.lower())
        if prons:
            num_syllables = None
            for pron in prons:
                count = 0
                for syllable in pron:
                    if 0 <= ord(syllable[-1]) - ord('0') <= 9:
                        count += 1
                if not num_syllables or num_syllables > count:
                    num_syllables = count
            return count
        return 1

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """
        prons1 = prondict.get(a.lower())
        prons2 = prondict.get(b.lower())
        if not prons1 or not prons2:
            return False
        for pr1 in prons1:
            for pr2 in prons2:
                if self.rhymes_pron(pr1, pr2):
                    return True
        return False

    def rhymes_pron(self, pr1, pr2):
        pr1 = [i for i in pr1]
        pr2 = [i for i in pr2]
        for i in range(len(pr1)):
            if 0 <= ord(pr1[i][-1]) - ord('0') <= 9:
                break
        pr1 = pr1[i:]
        for i in range(len(pr2)):
            if 0 <= ord(pr2[i][-1]) - ord('0') <= 9:
                break
        pr2 = pr2[i:]
        for ind in range(-1, -min(len(pr1), len(pr2)) - 1, -1):
            if pr1[ind] != pr2[ind]:
                return False
        return True

    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """
        if not text: return False
        sentences = text.split('\n')
        numsy = []
        last = []
        for sentence in sentences:
            count = 0
            words = word_tokenize(sentence)
            for w in words:
                if w not in punctuation:
                    count += self.num_syllables(w)
            if count != 0:
                numsy.append(count)
            for w in words[::-1]:
                if w not in punctuation:
                    last.append(w)
                    break
        if len(numsy) != 5: return False
        for x in numsy:
            if x < 4: return False
        if max(numsy[0], numsy[1], numsy[4]) - min(numsy[0], numsy[1], numsy[4]) > 2:
            return False
        if max(numsy[2], numsy[3]) - min(numsy[2], numsy[3]) > 2:
            return False
        if min(numsy[0], numsy[1], numsy[4]) <= max(numsy[2], numsy[3]):
            return False
        if not (self.rhymes(last[0], last[1]) and self.rhymes(last[1], last[4]) and \
                        self.rhymes(last[0], last[4])):
            return False
        if not self.rhymes(last[2], last[3]):
            return False
        if self.rhymes(last[1], last[2]):
            return False
        return True

    def apostrophe_tokenize(self, text):
        tokens = word_tokenize(text)
        res = []
        for t in tokens:
            if '\'' in t and len(res) > 0:
                res[len(res)-1] = res[len(res)-1]+t
            else:
                res.append(t)
        return res

    def guess_syllables(self, word):
        prons = prondict.get(word.lower())
        if prons:
            return self.num_syllables(word)
        if len(word) == 0: return 0
        if len(word) == 1: return 1
        vowels = 'aeiou'
        count = 0
        continuous_vowel = False
        for ind in range(len(word)):
            if word[ind] == 'y' and ind != 0 and word[ind-1] in 'bcdfhklmnprstz':
                count += 1
                continuous_vowel = True
            elif word[ind] not in vowels:
                continuous_vowel = False
            elif word[ind] in vowels and not continuous_vowel and ind != len(word)-1:
                count += 1
                continuous_vowel = True
        return count



# The code below should not need to be modified
def main():
    parser = argparse.ArgumentParser(
        description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addonoffarg(parser, 'debug', help="debug mode", default=False)
    parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help="output file")

    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    infile = prepfile(args.infile, 'r')
    outfile = prepfile(args.outfile, 'w')

    ld = LimerickDetector()
    lines = ''.join(infile.readlines())
    outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))


if __name__ == '__main__':
    main()


