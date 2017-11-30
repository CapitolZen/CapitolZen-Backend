from elasticsearch_dsl import analyzer
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
    sponsors = fields.NestedField()
    action_dates = fields.ObjectField()
    companions = fields.NestedField()
    votes = fields.ObjectField()
    sources = fields.ObjectField()
    documents = fields.ObjectField()
    bill_versions = fields.NestedField()
    bill_text = fields.TextField()
    bill_text_analysis = fields.ObjectField()

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
            'title',
            'summary',
            'type',
            'content',
        ]
