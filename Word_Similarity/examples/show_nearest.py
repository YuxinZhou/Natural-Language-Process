#!/usr/bin/env python
import distsim

word_to_vec_dict = distsim.load_word2vec("../nyt_word2vec.4k")
for i, (word, score) in enumerate(distsim.show_nearest(word_to_vec_dict, word_to_vec_dict['company'], set(['company']),distsim.cossim_dense), start=1):
    print("{}: {} ({})".format(i, word, score))
