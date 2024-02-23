import json
import pickle
from utils import tokenize, Postings, PostingList, process_verbs, normalize
from hazm import Lemmatizer
import time

# Read the JSON file
with open('IR_data_news_5k.json', 'r', encoding='utf-8') as file:
    data = file.read()

# Decode Unicode escape sequences
decoded_data = json.loads(data)

content_dataset, url_dataset, title_dataset = {}, {}, {}
for index, data in decoded_data.items():
    content_dataset[index] = data['content']
    url_dataset[index] = data['url']
    title_dataset[index] = data['title']


def load_data():
    dbfile = open('positional_indexes_file', 'rb')
    db = pickle.load(dbfile)
    dbfile.close()
    return db['positional_indexes']


def load_champion_list():
    dbfile = open('champion_list_file', 'rb')
    db = pickle.load(dbfile)
    dbfile.close()
    return db['champion_list']


positional_indexes = load_data()
champion_list = load_champion_list()

lemmatizer = Lemmatizer()


def get_query_tokens(query):
    normalize_query = normalize(query)
    query_tokens = tokenize(normalize_query)
    query_tokens = process_verbs(query_tokens)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in query_tokens]
    return lemmatized_tokens


def calculate_score(indexes, query_tokens):
    doc_scores = {}
    for query_token in query_tokens:
        posting_list = indexes[query_token]
        for k, v in posting_list.postings.items():
            if k in doc_scores.keys():
                doc_scores[k] += v.tf_idf
            else:
                doc_scores[k] = v.tf_idf
    return doc_scores


def top_k_docs(doc_scores, k):
    sorted_doc_scores = dict(sorted(doc_scores.items(), key=lambda item: item[1], reverse=True))
    return dict(list(sorted_doc_scores.items())[:k])


while True:
    query = input('type your query to search\n')
    if query == 'end':
        break
    try:
        time1 = time.time()
        query_tokens = get_query_tokens(query)
        #doc_scores = calculate_score(positional_indexes, query_tokens)
        doc_scores = calculate_score(champion_list, query_tokens)
        sorted_doc_scores = top_k_docs(doc_scores, 2)
        time2 = time.time()
        print(time1)
        print(time2)
        print(time2 - time1)
        for k in sorted_doc_scores.keys():
            print('Title: {title}'.format(title=title_dataset[k]))
            print('Score: {score}'.format(score=sorted_doc_scores[k]))
            print('Link: {url}'.format(url=url_dataset[k]))
            print('Content: {content}'.format(content=content_dataset[k]))
    except:
        print('there is no doc to retrieve\n')
