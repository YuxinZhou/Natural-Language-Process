# Applied Natural-Language-Process

A collection of interesting applied NLP tasks  

## Word Similarity

This module implements comparison functions for word representations and uses the functions and representations to solve semantic similarity tasks.  

It supports similarity queries and analogical reasoning tasks.  

`show_nearest()` finds the 10 words most similar to w. Display the similar words, and their similarity scores against the query word w. An example input queries:  
```
company
```
Output: 
```
1: firm (0.739202104486)
2: corporation (0.733216121624)
3: agency (0.690310755928)
4: unit (0.636080696538)
5: industry (0.63310344963)
6: microsoft (0.629542189259)
7: companies (0.60371111139)
8: wal-mart (0.593336821926)
9: sony (0.581199666729)
10: product (0.569321059484)
```

An interesting thing you can do with our module is perform analogical reasoning tasks. An example input:
```
king : man :: {} : woman
```

Output:
```
king : man :: Queen : woman
```

See how to use it from the folder “example”


## Authorship Identification
The aim of this project is to do authorship identification on lines of poetry written by Emily Bronte and William Shakespeare. We use the Naive Bayes classifier provided by nltk.  

#### About the Data
train set:  
	* s.data Lines of poetry by Shakespeare, marked with an ’s’   
 	* b.data Lines of poetry by Bronte, marked with an ’b’  
dev set:   
	* dev.tsv Lines of poetry mixed of Shakespeare and Bronte  


#### Usage
To begin with you should prepare the training data:
	```
   cat s.data b.data | python maketsv.py -o train.tsv
	```
You can then run the classifier:
	```
   python classify.py -i train.tsv
   	```
You should see output like:
```

Training classifier ...
Accuracy on dev: 0.971351
No test file passed; stopping.
```

## CKY parser
In this assignment we build a simple constituency parser trained from the ATIS portion of the Penn Treebank.

#### About the Data
Train set & preprocess  
The file train.trees contains a sequence of trees, one per line, each in the following format:
```
  (TOP (S (VP (VB Book) (NP (DT that) (NN flight)))) (PUNC .))
```
* Running `train.trees` through `preprocess.py` makes the trees strictly binary branching.   
* Running `postprocess.py` reverses all the modifications made by preprocess.py.  
* Running `train.trees` through `unknown.py` replaces all words that occurred only once with the special symbol <unk>.  

Dev set
The file dev.string contains a sequence of sentences, e.g.:
```
The flight should be eleven a.m tomorrow .
```
And the file dev.tree contains a sequence of trees respectively, e.g.:
```
(TOP (S (NP (DT The) (NN flight)) (VP (MD should) (VP (VB be) (NP (NP* (CD eleven) (RB a.m)) (NN tomorrow))))) (PUNC .))
```

#### Usage

python evalb.py dev.parses.post dev.trees







