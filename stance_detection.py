# -*- coding: utf-8 -*-

# import training data
# build features
# train naive bayes' classifer on features

# features: Jaccard similarity.
#   for sentence in body:
#       compute and store Jaccard similarity between body and sentence
#   compute average and maximum Jaccard similarity for the body
# The features passed to the classifier will be:
# ● the number of bigram and trigram
# repetitions between the article and
# headline, normalized by the length of
# the article or headline (whichever is
# longest).
# ● The average and maximum Jaccard
# similarities between the headline and
# each sentence in the article body (two
# numbers).

# TODO: add stemming, lowercase everything?, replace bad characters

import pdb
import string
from csv import DictReader
import nltk
from sklearn.metrics import jaccard_similarity_score


class StanceDetectionClassifier:
    REMOVE_PUNC_MAP = dict((ord(char), None) for char in string.punctuation)

    def __init__(self):
        self._features = []

    def gen_training_features(self, bodies_fpath, stances_fpath):
        self._read(bodies_fpath, stances_fpath)
        unigrams = self._train_ngrams(1)
        self._gen_jaccard_sims()

    def _gen_jaccard_sims(self):
        # currently assumes both body and headline are longer than 0.
        punc_rem_tokenizer = nltk.RegexpTokenizer(r'\w+')

        self.avg_and_max_sims = []

        for st in self._stances:
            body = self._bodies[st['Body ID']]
            headline = st['Headline']
            headline = headline.translate(self.REMOVE_PUNC_MAP)
            headline = nltk.word_tokenize(headline)
            sents = nltk.sent_tokenize(body)
            sents = self._remove_punctuation(sents)
            sents = self._word_tokenize(sents)
            num_sents = len(sents)
            jacc_sims = []
            for sent in sents:
                if len(sent) < 1:
                    continue
                # extend shorter word list so that both are the same length
                len_diff = len(headline) - len(sent)
                headline_cpy = headline
                sent_cpy = sent

                if len_diff < 0: # sent longer than headline
                    headline_cpy = headline_cpy + ([headline_cpy[-1]] * abs(len_diff))
                elif len_diff > 0: # headline longer than sent
                    sent_cpy = sent_cpy + ([sent_cpy[-1]] * abs(len_diff))

                jacc_sims.append(jaccard_similarity_score(headline_cpy, sent_cpy))
            avg_sim = sum(jacc_sims) / len(jacc_sims)
            max_sim = max(jacc_sims)
            self.avg_and_max_sims.append([avg_sim, max_sim])

    def _word_tokenize(self, str_list):
        return map(lambda s: nltk.word_tokenize(s), str_list)

    def _remove_punctuation(self, str_list):
        return map(lambda s: s.translate(self.REMOVE_PUNC_MAP), str_list)

    def _read(self, bodies_fpath, stances_fpath):
        with open(bodies_fpath, 'r') as f:
            r = DictReader(f)
            self._bodies = {}
            for line in r:
                body = line['articleBody'].decode('utf-8')
                self._bodies[int(line['Body ID'])] = body

        with open(stances_fpath, 'r') as f:
            r = DictReader(f)
            self._stances = []
            for line in r:
                headline = line['Headline'].decode('utf-8')
                stance = line['Stance'].decode('utf-8')
                body_id = int(line['Body ID'])
                self._stances.append({
                        'Headline': headline,
                        'Body ID': body_id,
                        'Stance': stance})

    def _get_ngrams(self, text, n):
        tokens = nltk.word_tokenize(text)
        tokens = [ token.lower() for token in tokens if len(token) > 1 ]
        return nltk.ngrams(tokens, n)

    def _train_ngrams(self, n):
        stance_similarities = []
        body_bigrams = {}

        for bodyId in self._bodies:
            body_bigrams[bodyId] = self._get_ngrams(self._bodies[bodyId], n)

        for stance in self._stances:
            stance_bigrams = self._get_ngrams(stance['Headline'], n)
            num_bigrams_common = 0
            for bigram in stance_bigrams:
                if bigram in body_bigrams[stance['Body ID']]:
                    num_bigrams_common += 1
            stance_similarities.append(num_bigrams_common)

        # normalize the counts based on length of the article
        for i in range(len(stance_similarities)):
            body_id = self._stances[i]['Body ID']
            stance_similarities[i] = float(stance_similarities[i])/len(self._bodies[body_id])

        return stance_similarities

    def train(self):
        pass

    def predict(self, bodies_fpath, stances_fpath):
        pass

cls = StanceDetectionClassifier()
cls.gen_training_features('training_data/train_bodies.csv',
        'training_data/train_stances.csv')
