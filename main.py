import json
import math
import pickle
from utils import tokenize, Postings, PostingList, process_verbs, normalize

from hazm import Lemmatizer

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

content_dataset = {key: normalize(value) for key, value in content_dataset.items()}

lemmatizer = Lemmatizer()

positional_indexes = {}
for index, content in content_dataset.items():
    tokens = tokenize(content)
    tokens = process_verbs(tokens)
    for position, token in enumerate(tokens):
        if token in positional_indexes.keys():
            positional_indexes[token].frequency += 1
            if index not in positional_indexes[token].postings.keys():
                postings = Postings()
                positional_indexes[token].postings[index] = postings
            positional_indexes[token].postings[index].frequency += 1
            positional_indexes[token].postings[index].positions.append(position)
        else:
            positional_indexes[token] = PostingList()
            positional_indexes[token].frequency += 1
            postings = Postings()
            postings.frequency += 1
            postings.positions.append(position)
            positional_indexes[token].postings[index] = postings


def merge_posting_lists(first_posting_list: PostingList, second_posting_list: PostingList):
    merged_posting_list = PostingList()
    merged_posting_list.frequency = first_posting_list.frequency + second_posting_list.frequency
    key_set1 = set(first_posting_list.postings.keys())
    key_set2 = set(second_posting_list.postings.keys())
    intersection_keys = key_set1.intersection(key_set2)
    for key in intersection_keys:
        merged_postings = Postings()
        postings1 = first_posting_list.postings[key]
        postings2 = second_posting_list.postings[key]
        merged_postings.frequency = postings1.frequency + postings2.frequency
        merged_positions = []
        merged_positions.extend(postings1.positions)
        merged_positions.extend(postings2.positions)
        merged_positions.sort(key=lambda x: x)
        merged_postings.positions = merged_positions
        merged_posting_list.postings[key] = merged_postings
    key_set1 = key_set1 - intersection_keys
    for key in key_set1:
        merged_posting_list.postings[key] = first_posting_list.postings[key]
    key_set2 = key_set2 - intersection_keys
    for key in key_set2:
        merged_posting_list.postings[key] = second_posting_list.postings[key]
    return merged_posting_list


lemmatized_positional_indexes = {}
for term in positional_indexes.keys():
    lemmatized_term = lemmatizer.lemmatize(term)
    if lemmatized_term not in lemmatized_positional_indexes.keys():
        lemmatized_positional_indexes[lemmatized_term] = positional_indexes[term]
    else:
        lemmatized_positional_indexes[lemmatized_term] = (
            merge_posting_lists(lemmatized_positional_indexes[lemmatized_term], positional_indexes[term]))

positional_indexes = dict(sorted(positional_indexes.items(), key=lambda item: item[1].frequency, reverse=True))

positional_indexes = dict(list(positional_indexes.items())[50:])


def tf_idf(term, doc_id):
    f_t_in_d = positional_indexes[term].postings[doc_id].frequency
    n = len(content_dataset)
    n_t = len(positional_indexes[term].postings.keys())
    return (1 + math.log(f_t_in_d, 10)) * math.log(n / n_t)


doc_lengths = {}
for k, v in positional_indexes.items():
    for doc_id in v.postings.keys():
        doc_tf_idf = tf_idf(k, doc_id)
        v.postings[doc_id].tf_idf += doc_tf_idf
        if doc_id in doc_lengths.keys():
            doc_lengths[doc_id] += doc_tf_idf ** 2
        else:
            doc_lengths[doc_id] = doc_tf_idf ** 2

for doc_id, length in doc_lengths.items():
    normalized_length = math.sqrt(length) if length > 0 else 1
    for term in positional_indexes.values():
        if doc_id in term.postings.keys():
            term.postings[doc_id].tf_idf /= normalized_length

champion_list = {}
for k, v in positional_indexes.items():
    postings = v.postings
    champion_posting = dict(sorted(postings.items(), key=lambda item: item[1].tf_idf, reverse=True))
    champion_list[k] = PostingList()
    champion_list[k].frequency = v.frequency
    champion_list[k].postings = dict(list(champion_posting.items())[:20])


def save_data():
    db = {}
    db['positional_indexes'] = positional_indexes
    dbfile = open('positional_indexes_file', 'ab')
    pickle.dump(db, dbfile)
    dbfile.close()


def save_champion_list():
    db = {}
    db['champion_list'] = champion_list
    dbfile = open('champion_list_file', 'ab')
    pickle.dump(db, dbfile)
    dbfile.close()


save_data()
save_champion_list()

