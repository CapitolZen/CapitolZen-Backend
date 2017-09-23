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
    current_committee = fields.ObjectField(properties={
        'name': fields.StringField(),
        'state': fields.StringField(),
        'chamber': fields.StringField(),
        'remote_id': fields.StringField(),
        'parent_id': fields.StringField(),
        'subcommittee': fields.StringField()
    })
    sponsor = fields.ObjectField(properties={
        'remote_id': fields.StringField(),
        'state': fields.StringField(),
        'active': fields.BooleanField(),
        'chamber': fields.StringField(),
        'party': fields.StringField(),
        'district': fields.StringField(),
        'email': fields.StringField(),
        'url': fields.StringField(),
        'photo_url': fields.StringField(),
        'first_name': fields.StringField(),
        'middle_name': fields.StringField(),
        'last_name': fields.StringField(),
        'suffixes': fields.StringField()
    })
    history = fields.ObjectField()
    action_dates = fields.ObjectField()
    cosponsors = fields.ObjectField()
    companions = fields.NestedField()
    categories = fields.NestedField()
    votes = fields.ObjectField()
    sources = fields.ObjectField()
    documents = fields.ObjectField()
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
            'type',
            'status',
            'title',
            'summary',
        ]

    def prepare_id(self, instance):
        return str(instance.id)

    def prepare_summary(self, instance):
        # do something here to generate a human readable summary
        return instance.summary
