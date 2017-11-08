from logging import getLogger

import nltk

from django.apps import AppConfig

logger = getLogger("cz_logger")


class DocumentAnalysisConfig(AppConfig):
    name = 'capitolzen.document_analysis'

    def ready(self):
        nltk_data = [
            'punkt', 'abc', 'city_database', 'cmudict', 'comparative_sentences',
            'inaugural', 'names', 'paradigms', 'pros_cons', 'sentence_polarity',
            'shakespeare', 'state_union', 'stopwords', 'subjectivity',
            'words', 'book_grammars', 'large_grammars',
        ]

        # Populate nltk library
        try:
            nltk.download(nltk_data, halt_on_error=False, quiet=True)
        except Exception as e:
            logger.exception(e)
