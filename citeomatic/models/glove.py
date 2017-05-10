import io

import numpy as np
from citeomatic.features import CLEAN_TEXT_RE


class GloveModel(object):
    """
    A model to sum over pre-trained Glove vectors.

    """

    def __init__(self):
        self.d = None
        self.embeddings = None

    def fit(self, path, featurizer):
        self.d = int(path.split('.')[-2][:-1])
        wi = featurizer.word_indexer.word_to_index
        self.embeddings = np.zeros((np.max(list(wi.values())) + 1, self.d))
        with io.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line_split = line.strip().split()
                word, the_rest = self.clean(line_split[0]), line_split[1:]
                if word in wi:
                    self.embeddings[wi[word], :] = np.array(the_rest
                                                           ).astype(np.float32)

    def predict(self, X):
        title_inds_all_a, abstract_inds_all_a, title_inds_all_b, abstract_inds_all_b = X
        embedding_sums_a = self._inds_to_vec(
            title_inds_all_a, abstract_inds_all_a
        )
        embedding_sums_b = self._inds_to_vec(
            title_inds_all_b, abstract_inds_all_b
        )
        preds = np.sum(embedding_sums_a * embedding_sums_b, axis=1)
        return [preds, np.zeros(preds.shape), preds]

    def _inds_combine(self, title_inds, abstract_inds):
        return list(title_inds[title_inds > 0]
                   ) + list(abstract_inds[abstract_inds > 0])

    def _inds_to_vec(self, title_inds_all, abstract_inds_all):
        n_docs = len(title_inds_all)
        result = np.zeros((n_docs, self.d))
        for i in range(n_docs):
            inds = self._inds_combine(title_inds_all[i], abstract_inds_all[i])
            embedding_sum = np.sum(self.embeddings[np.array(inds), :], 0)
            result[i, :] = embedding_sum / np.linalg.norm(embedding_sum)
        return result

    def clean(self, text):
        return CLEAN_TEXT_RE.sub(' ', text.lower())
