from json import loads
from numpy import asarray
from os.path import isfile
from itertools import chain, repeat
from collections import defaultdict
from gensim.models import LdaModel, LsiModel, Doc2Vec
from gensim.corpora import Dictionary, MmCorpus
from gensim.similarities import MatrixSimilarity
from sklearn.linear_model import LogisticRegression

def iterate_summaries(docs):
    for doc in docs:
        yield iterate_words(doc.get("summary"))

def iterate_words(line):
    prepositions = {"a", "an", "and", "as", "at", "by", "for", "he", "her", "his", "in", "into", "if", "is", "it", "its", "like", "of", "on", "over", "she", "that", "the", "these", "those", "though", "to", "up", "upon", "was", "were", "will", "with", "who", "whose", "would"}
    freq = defaultdict(int)

    for word in line.lower().split():
        freq["word"] += 1
        if word not in prepositions and len(word) > 2 and freq["word"] > 2:
            yield word

def hoist_dict(listofdicts, key):
    return {d.get(key): d for d in listofdicts}

class Model:
    def __init__(self, filename):
        self.docs = loads(open(filename, "r").read())
        self.docmap = hoist_dict(self.docs, "id")

        if isfile("data.dict"):
            self.dictionary = Dictionary.load("data.dict")
        else:
            self.dictionary = Dictionary(iterate_summaries(self.docs))
            self.dictionary.save("data.dict")

        if isfile("data.mm"):
            self.corpus = MmCorpus("data.mm")
        else:
            self.corpus = (self.dictionary.doc2bow(text) for text in iterate_summaries(self.docs))
            MmCorpus.serialize("data.mm", self.corpus)
            self.corpus = MmCorpus("data.mm")
            # self.corpus.serialize("data.mm")

        self.lsi = LsiModel(self.corpus, id2word=self.dictionary, num_topics=3)

        if isfile("data.sim"):
            self.sim = MatrixSimilarity.load("data.sim")
        else:
            self.sim = MatrixSimilarity(self.lsi[self.corpus])
            self.sim.save("data.sim")

        # self.lda = LdaModel(corpus=self.corpus, id2word=self.dictionary, num_topics=100, update_every=1, chunksize=10000, passes=1)

        self.sentiment_model = Doc2Vec.load("./imdb.d2v")
        self.sentiment = LogisticRegression()
        self.sentiment.fit([self.sentiment_model.docvecs["TEST_POS_" + str(i)] for i in range(12500)] +
                           [self.sentiment_model.docvecs["TEST_NEG_" + str(i)] for i in range(12500)],
                           asarray(list(chain(repeat(0, 12500), repeat(1, 12500)))))

    def similar(self, doc):
        return [{**{"similarity": sim}, **doc}
                for doc, sim in zip(self.docs, self.sim[self.lsi[self.dictionary.doc2bow(doc.lower().split())]])]

    def sentiment(self, id):
        # TODO: Gensim
        import random
        return random.uniform(0, 1)

    def doc(self, id):
        return self.docmap.get(id)
