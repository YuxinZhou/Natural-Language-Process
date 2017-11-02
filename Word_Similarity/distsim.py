from __future__ import division
import sys, json, math
import os
import numpy as np


def load_word2vec(filename):
    # Returns a dict containing a {word: numpy array for a dense word vector} mapping.
    # It loads everything into memory.

    w2vec = {}
    with open(filename, "r") as f_in:
        for line in f_in:
            line_split = line.replace("\n", "").split()
            w = line_split[0]
            vec = np.array([float(x) for x in line_split[1:]])
            w2vec[w] = vec
    return w2vec


def load_contexts(filename):
    # Returns a dict containing a {word: contextcount} mapping.
    # It loads everything into memory.

    data = {}
    for word, ccdict in stream_contexts(filename):
        data[word] = ccdict
    print "file %s has contexts for %s words" % (filename, len(data))
    return data


def stream_contexts(filename):
    # Streams through (word, countextcount) pairs.
    # Does NOT load everything at once.
    # This is a Python generator, not a normal function.
    for line in open(filename):
        word, n, ccdict = line.split("\t")
        n = int(n)
        ccdict = json.loads(ccdict)
        yield word, ccdict


def cossim_sparse(v1, v2):
    # Take two context-count dictionaries as input
    # and return the cosine similarity between the two vectors.
    # Should return a number beween 0 and 1

    factor = 0
    v1sqaure = 0
    v2sqaure = 0
    for key in v1:
        v1sqaure += v1[key] * v1[key]
        if key in v2:
            factor += v1[key] * v2[key]
    for key in v2:
        v2sqaure += v2[key] * v2[key]
    return float(factor) / (np.sqrt(v1sqaure) * np.sqrt(v2sqaure))


def cossim_dense(v1, v2):
    # v1 and v2 are numpy arrays
    # Compute the cosine simlarity between them.
    # Should return a number between -1 and 1
    factor = 0
    v1sqaure = 0
    v2sqaure = 0
    assert len(v1) == len(v2)
    for idx in range(len(v1)):
        factor += v1[idx] * v2[idx]
        v1sqaure += v1[idx] * v1[idx]
        v2sqaure += v2[idx] * v2[idx]
    return float(factor) / (np.sqrt(v1sqaure) * np.sqrt(v2sqaure))


def show_nearest(word_2_vec, w_vec, exclude_w, sim_metric):
    # word_2_vec: a dictionary of word-context vectors. The vector could be a sparse (dictionary) or dense (numpy array).
    # w_vec: the context vector of a particular query word `w`. It could be a sparse vector (dictionary) or dense vector (numpy array).
    # exclude_w: the words you want to exclude in the responses. It is a set in python.
    # sim_metric: the similarity metric you want to use. It is a python function
    # which takes two word vectors as arguments.

    # return: an iterable (e.g. a list) of up to 10 tuples of the form (word, score) where the nth tuple indicates the
    # nth most similar word to the input word and the similarity score of that word and the input word
    # if fewer than 10 words are available the function should return a shorter iterable
    #
    # example:
    # [(cat, 0.827517295965), (university, -0.190753135501)]
    ans = []
    for key in word_2_vec:
        if key not in exclude_w:
            sim = sim_metric(word_2_vec[key], w_vec)
            ans.append((key, sim))
    ans.sort(key=lambda (x, y): y, reverse=True)
    if len(ans) > 10:
        ans = ans[:10]
    return ans
