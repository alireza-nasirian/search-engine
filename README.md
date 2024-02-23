# search-engine

This repository contains the code for an Information Retrieval project, part of the Information Retrieval course at Amirkabir University of Technology.
The project is supervised by Dr. Nik Abadi.

## Overview

The project is an information retrieval engine that uses the [hazm](https://github.com/roshan-research/hazm.git) library. It employs techniques such as normalization and stemming to create a positional index for its dataset.

## Dataset
The project's dataset is about 12000 news articles from different persian new agencies, in following format : 

```json
{
  "title": "Article Title",
  "content": "New Content",
  "url": "URL to Article",
}
```

## Implementation
This phase includes 4 tasks : 

- Processing dataset artcles in order to create the positional index
- Creating positional index using processed docs
- Enhancing positional index and Query Processing Unit to support ranked retreival
- Increasing efficiency using index elimination and champion lists



### Task 1
In this task, articles are loaded, normalized, tokenized and stemmed, stop words are also deleted from tokens.
the outpu of this task is a hashmap, relating each docID with a list of processed tokens.

### Task 2
In this task processed tokens are traversed to create a positional index. In this positional index,
we keep for each term, its overall frequency and postings lists of docs that contains this term.
In each postings list we keep for each doc, its docID, frequency of the term in the doc and a list of positions of term in the document.

### Task 3
In this task, we enhance positional index to store IDF for each term and TF for each Doc_Term pair.
we can then use this enhanced version to implement Cosine and Jacquard similarity functions. <br>

IDF Formula :
```python
  IDF = math.log10(allDocsCount/ docFrequency)
```
TF Formula :
```python
  TF = (1 + math.log10(docNum))
```

### Task 4
To decrease the delay of Query Processing, we implement "Champion Lists" and use "Index Elimination"
to prune the docs that are less likely to end up in the "Top-K" list.
