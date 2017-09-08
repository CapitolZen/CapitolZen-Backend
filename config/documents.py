from django_elasticsearch_dsl import DocType, fields


class BaseIndex(DocType):

    class Meta:
        abstract = True
        fields = [
            'id',
            'created',
            'modified',
            'doc_type'
        ]
