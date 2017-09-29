#!/usr/bin/env python
from collections import defaultdict
from csv import DictReader, DictWriter

import nltk
import codecs
import sys
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer



kTOKENIZER = TreebankWordTokenizer()

def morphy_stem(word):
    """
    Simple stemmer
    """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()


class FeatureExtractor:
    def __init__(self):
        self.Punctuation = [',', '.', '?', ':', ';', '!']
        Prepositions = ['of', 'at', 'in', 'without', 'between']
        Pronouns = ['he', 'they', 'anybody', 'it', 'one', 'you', 'thou', 'thee']
        Determiners = ['the', 'a', 'that', 'my', 'more', 'much', 'either', 'neither', 'thy']
        Conjunctions = ['and', 'that', 'when', 'while', 'although', 'or', 'doth']
        Auxiliaryverbs = ['be', 'is', 'am', 'are', 'have', 'do', 'was', 'were']
        Particles = ['no', 'not', 'nor', 'as']
        self.Special_char = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~1234567890'
        self.Typo = '10<>*'
        self.prondict = nltk.corpus.cmudict.dict()
        self.Function_words = Prepositions + Pronouns + Determiners + \
                              Conjunctions + Auxiliaryverbs


    def num_syllables(self, word):
        prons = self.prondict.get(word.lower())
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
        return self.guess_syllables(word.lower())

    def guess_syllables(self, word):
        if len(word) == 0 or word in self.Punctuation: return 0
        if len(word) == 1: return 1
        vowels = 'aeiou'
        count = 0
        continuous_vowel = False
        for ind in range(len(word)):
            if word[ind] == 'y' and ind != 0 and word[ind - 1] in 'bcdfhklmnprstz':
                count += 1
                continuous_vowel = True
            elif word[ind] not in vowels:
                continuous_vowel = False
            elif word[ind] in vowels and not continuous_vowel and ind != len(word) - 1:
                count += 1
                continuous_vowel = True
        return count

    def features(self, text):
        d = defaultdict(int)
        tokens = kTOKENIZER.tokenize(text)
        words = map(lambda x: x[:-1] if x[-1] in self.Special_char else x, \
                        text.split())
        # if text[-1] == ' ':
        #     d['xuanxue'] += 1
        words = filter(lambda x: len(x) != 0, words)
        syllables = [self.num_syllables(x) for x in words]
        d['num_syllables'] = sum(syllables)
        d['syllables_list'] = tuple(syllables)

        if ' ;' in text or ' !' in text or ' ?' in text or ' :' in text:
            d['format_feature'] += 1

        for ii in kTOKENIZER.tokenize(text):
            if ii not in self.Function_words and ii not in self.Punctuation:
                d[morphy_stem(ii)] += 1

        # function_words = filter(lambda x: x.lower() in self.Function_words, tokens)

        word_len = map(lambda x: len(x) - 1 if x[-1] in self.Special_char else len(x), \
                       text.split())
        word_len = filter(lambda x: x != 0, word_len)
        mean = sum(word_len) / float(len(word_len))
        std = sum([(x - mean) ** 2 for x in word_len])
        #
        # 70%
        # d['function_pct'] = len(function_words) / float(len(tokens))

        d['word_mean'] = mean
        d['word_std'] = std
        # # print [self.prondict.get(x) for x in tokens]
        # #
        # 74-76%
        upper_letter = filter(lambda x: x not in self.Special_char and x != ' ' and \
                                        x == x.upper() and x != 'I', [ii for ii in text])
        if len(upper_letter) - 1 > 0:
            d['upper_letter'] = 1

        #
        # # 73-78%
        # punctuation = filter(lambda x: x in self.Punctuation, [ii for ii in text])
        # d['punctuation_pct'] = len(punctuation) / float(len(words))






        return d



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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--trainfile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help="input train file")
    parser.add_argument("--testfile", "-t", nargs='?', type=argparse.FileType('r'), default=None,
                        help="input test file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help="output file")
    parser.add_argument('--subsample', type=float, default=1.0,
                        help='subsample this fraction of total')
    args = parser.parse_args()
    trainfile = prepfile(args.trainfile, 'r')
    if args.testfile is not None:
        testfile = prepfile(args.testfile, 'r')
    else:
        testfile = None
    outfile = prepfile(args.outfile, 'w')

    # Create feature extractor (you may want to modify this)
    fe = FeatureExtractor()

    # Read in training data
    train = DictReader(trainfile, delimiter='\t')

    # Split off dev section
    dev_train = []
    dev_test = []
    full_train = []

    for ii in train:
        if args.subsample < 1.0 and int(ii['id']) % 100 > 100 * args.subsample:
            continue
        feat = fe.features(ii['text'])
        if int(ii['id']) % 5 == 0:
            dev_test.append((feat, ii['cat']))
        else:
            dev_train.append((feat, ii['cat']))
        full_train.append((feat, ii['cat']))

    # Train a classifier
    sys.stderr.write("Training classifier ...\n")
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train)

    right = 0
    total = len(dev_test)
    for ii in dev_test:
        prediction = classifier.classify(ii[0])
        if prediction == ii[1]:
            right += 1

    sys.stderr.write("Accuracy on dev: %f\n" % (float(right) / float(total)))

    if testfile is None:
        sys.stderr.write("No test file passed; stopping.\n")
    else:
        # Retrain on all data
        classifier = nltk.classify.NaiveBayesClassifier.train(dev_train + dev_test)

        # Read in test section
        test = {}
        for ii in DictReader(testfile, delimiter='\t'):
            test[ii['id']] = classifier.classify(fe.features(ii['text']))

        # Write predictions
        o = DictWriter(outfile, ['id', 'pred'])
        o.writeheader()
        for ii in sorted(test):
            o.writerow({'id': ii, 'pred': test[ii]})
