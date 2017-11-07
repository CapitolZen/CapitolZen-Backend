from logging import getLogger

import nltk

from django.apps import AppConfig

logger = getLogger("cz_logger")


class DocumentAnalysisConfig(AppConfig):
    name = 'capitolzen.document_analysis'

    def ready(self):
        nltk_data = []

        # Populate nltk library
        try:
            nltk.download(nltk_data, halt_on_error=False, quiet=True)
        except Exception as e:
            logger.exception(e)
