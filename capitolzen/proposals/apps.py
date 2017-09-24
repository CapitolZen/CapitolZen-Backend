from __future__ import unicode_literals
from elasticsearch import Elasticsearch, RequestsHttpConnection

from django.apps import AppConfig
from django.conf import settings


class ProposalsConfig(AppConfig):
    name = 'capitolzen.proposals'
    label = 'proposals'
    verbose_name = 'Proposals'

    def ready(self):
        super()
        # This will throw a lot of errors but will eventually succeed
        # after migrations and everything have run
        es_client = Elasticsearch(
            hosts=settings.ELASTICSEARCH_DSL['default']['hosts'],
            connection_class=RequestsHttpConnection
        )
        response = es_client.index(
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
        print(response)

