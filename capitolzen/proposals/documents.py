from django_elasticsearch_dsl import Index, fields

from config.documents import BaseIndex

from capitolzen.proposals.models import Bill

bill = Index('bills')

# http://bit.ly/create-index
bill.settings(
    number_of_shards=3,
    number_of_replicas=2
)


@bill.doc_type
class BillDocument(BaseIndex):
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

    class Meta(BaseIndex.Meta):
        model = Bill

        fields = BaseIndex.Meta.fields + [
            'state',
            'state_id',
            'remote_id',
            'session',
            'history',
            'action_dates',
            'chamber',
            'type',
            'status',
            'cosponsors',
            'title',
            'companions',
            'categories',
            'votes',
            'summary',
            'sources',
            'documents',
            'bill_versions'
        ]

    def prepare_summary(self, instance):
        # do something here to generate a human readable summary
        return instance
