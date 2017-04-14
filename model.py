from os.path import isfile
from collections import defaultdict
from gensim.models import LdaModel, LsiModel
from gensim.corpora import Dictionary, MmCorpus
from gensim.similarities import MatrixSimilarity

def iterate_lines(filename):
    for line in open(filename, "r"):
        yield iterate_words(line)

def iterate_words(line):
    prepositions = {"a", "an", "and", "as", "at", "by", "for", "he", "her", "his", "in", "into", "if", "is", "it", "its", "like", "of", "on", "over", "she", "that", "the", "these", "those", "though", "to", "up", "upon", "was", "were", "will", "with", "who", "whose", "would"}
    freq = defaultdict(int)

    for word in line.lower().split():
        freq["word"] += 1
        if word not in prepositions and len(word) > 2 and freq["word"] > 2:
            yield word

class Model:
    def __init__(self, filename):
        if isfile("data.dict"):
            self.dictionary = Dictionary.load("data.dict")
        else:
            self.dictionary = Dictionary(iterate_lines(filename))
            self.dictionary.save("data.dict")

        if isfile("data.mm"):
            self.corpus = MmCorpus("data.mm")
        else:
            self.corpus = (self.dictionary.doc2bow(text) for text in iterate_lines(filename))
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

    def similar(self, doc):
        return self.sim[self.lsi[self.dictionary.doc2bow(doc.lower().split())]]
