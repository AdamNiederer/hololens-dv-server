from json import loads
from numpy import asarray
from random import shuffle
from os.path import isfile
from itertools import chain, repeat
from gensim.models import LdaModel, LsiModel, Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from gensim.corpora import Dictionary, MmCorpus
from gensim.similarities import MatrixSimilarity
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA

def iterate_summaries(docs):
    for doc in docs:
        yield iterate_words(doc.get("summary"))

def iterate_words(line):
    prepositions = {"a", "an", "and", "as", "at", "by", "for", "he", "her", "his", "in", "into", "if", "is", "it", "its", "like", "of", "on", "over", "she", "that", "the", "these", "those", "though", "to", "up", "upon", "was", "were", "will", "with", "who", "whose", "would"}
    for word in line.lower().split():
        if word not in prepositions and len(word) > 2:# and freq["word"] > 2:
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
            corpus = (self.dictionary.doc2bow(text) for text in iterate_summaries(self.docs))
            MmCorpus.serialize("data.mm", corpus)
            self.corpus = MmCorpus("data.mm")

        self.lsi = LsiModel(self.corpus, id2word=self.dictionary, num_topics=3)

        if isfile("data.sim"):
            self.sim = MatrixSimilarity.load("data.sim")
        else:
            self.sim = MatrixSimilarity(self.lsi[self.corpus])
            self.sim.save("data.sim")

        # self.lda = LdaModel(corpus=self.corpus, id2word=self.dictionary, num_topics=100, update_every=1, chunksize=10000, passes=1)

        self.sentiment_model = Doc2Vec.load("imdb.d2v")
        self.sentiment = LogisticRegression()
        self.sentiment.fit([self.sentiment_model.docvecs["TEST_POS_" + str(i)] for i in range(12500)] +
                           [self.sentiment_model.docvecs["TEST_NEG_" + str(i)] for i in range(12500)],
                           asarray(list(chain(repeat(0, 12500), repeat(1, 12500)))))

        if isfile("arxiv.d2v"):
            self.doc_model = Doc2Vec.load("arxiv.d2v")
        else:
            tagged = [TaggedDocument(doc.get("summary").split(), [doc.get("id")]) for doc in self.docs]
            doc_model = Doc2Vec(min_count=1, window=10, size=100, sample=1e-4, negative=5, workers=7)
            doc_model.build_vocab(tagged)
            shuffle(tagged) # Replace with functional stuff
            for epoch in range(10):
                doc_model.train(tagged, total_examples=doc_model.corpus_count, epochs=doc_model.iter)
            doc_model.save("arxiv.d2v")

    def similar(self, query):
        """ Return all documents with similarity scores for the given query """
        return [{**{"similarity": float(sim)}, **doc}
                for doc, sim in zip(self.docs, self.sim[self.lsi[self.dictionary.doc2bow(query.lower().split())]])]

    def sentiment(self, id):
        """ Return a sentiment score for this document. """
        # TODO: Gensim
        import random
        return random.uniform(0, 1)

    def doc(self, id):
        return self.docmap.get(id)

    @property
    def positions(self):
        """ Return the positions for all document. Coordinates are arbitrary,
        but similar documents are physically close. """
        vectors = [self.sentiment_model[s] for s in self.sentiment_model.wv.index2word]
        pca = PCA(n_components=3, whiten=True)
        return pca.fit(vectors).transform(vectors)

    @property
    def everything(self):
        """ Return all documents with coordinates and sentiment scores """
        # TODO: Sentiment
        return [{**{"coordinates": list(pos)}, **doc}
                for doc, pos in zip(self.docs, self.positions)]
