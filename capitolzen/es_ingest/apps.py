from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests.exceptions import ConnectionError

from django.apps import AppConfig
from django.conf import settings


class ESIngestConfig(AppConfig):
    name = 'capitolzen.es_ingest'

    def ready(self):
        try:
            # This will throw a lot of errors but will eventually succeed
            # after migrations and everything have run
            es_client = Elasticsearch(
                hosts=settings.ELASTICSEARCH_DSL['default']['hosts'],
                connection_class=RequestsHttpConnection
            )
            es_client.index(
                index='_ingest',
                doc_type='pipeline',
                id='attachment',
                body={
                    "description": "Extract attachment information",
                    "processors": [
                        {
                            "attachment": {
                                "field": "data",
                                "target_field": "bill_text",
                                "indexed_chars": -1
                            }
                        }
                    ]
                }
            )
        except ConnectionError:
            pass
