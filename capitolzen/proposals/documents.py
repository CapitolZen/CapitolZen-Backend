import base64
import requests

from elasticsearch_dsl import analyzer, Keyword
from django_elasticsearch_dsl import Index, fields, DocType

from capitolzen.proposals.models import Bill

html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)
bill = Index('bills')

# http://bit.ly/create-index
bill.settings(
    number_of_shards=3,
    number_of_replicas=2
)


@bill.doc_type
class BillDocument(DocType):
    id = fields.String()
    sponsors = fields.NestedField()
    action_dates = fields.ObjectField()
    companions = fields.NestedField()
    votes = fields.ObjectField()
    sources = fields.ObjectField()
    documents = fields.ObjectField()
    versions = fields.NestedField()
    bill_text = fields.TextField(
        analyzer=html_strip,
        fields={'raw': Keyword()}
    )

    class Meta:
        model = Bill

        fields = [
            'created',
            'modified',
            'state',
            'state_id',
            'remote_id',
            'session',
            'chamber',
            'status',
            'title',
            'summary',
            'type'
        ]

    def prepare_id(self, instance):
        return str(instance.id)

    def prepare_summary(self, instance):
        # do something here to generate a human readable summary
        return instance.summary

    def prepare(self, instance):
        parent = super()
        if not instance.current_version:
            return parent
        response = requests.get(instance.current_version)
        if 200 >= response.status_code < 300:
            content = response.content
        else:
            return parent
        doc_exists = self.connection.exists(
            index=str(self._doc_type.index),
            doc_type=self._doc_type.mapping.doc_type,
            id=instance.pk
        )
        if not doc_exists:
            self.connection.create(
                index=str(self._doc_type.index),
                doc_type=self._doc_type.mapping.doc_type,
                id=instance.pk,
                pipeline='attachment',
                body={
                    'data': base64.b64encode(content).decode('ascii')
                }
            )
        return parent
