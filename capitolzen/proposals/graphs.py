from py2neo import Graph
from rake_nltk import Rake
from nltk.tokenize import word_tokenize
from gensim import corpora, models, similarities

from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Search

from django.conf import settings

from capitolzen.proposals.models import Bill, Legislator
from capitolzen.proposals.documents import BillDocument


class BasicGraph(object):
    graph = Graph(**settings.GRAPH_DATABASE)
    instance = None
    instance_class = None

    def __init__(self, identifier):
        self.instance = self.instance_class.objects.get(id=identifier)

    def merge(self):
        raise NotImplementedError()

    def run(self):
        self.merge()


class BillGraph(BasicGraph):
    instance_class = Bill
    es_client = Elasticsearch(
        hosts=settings.ELASTICSEARCH_DSL['default']['hosts'],
        connection_class=RequestsHttpConnection
    )

    # Keyword score requirement
    # http://textminingonline.com/getting-started-with-keyword-extraction
    min_rank_score = 10.0

    # If no keywords are ranked above 10, how many keywords should we grab
    # from the generated list as a default
    default_list_length = 5
    related_docs = None

    def merge(self):
        query = """
            MERGE (bill:Bill {uuid: $uuid})
            ON CREATE SET bill.created = $created, 
                bill.modified = $modified, bill.state_id = $state_id, 
                bill.remote_id = $remote_id, bill.title = $title
            ON MATCH SET bill.modified = $modified,
                bill.title = $title
            RETURN bill
            """
        self.graph.data(query, parameters={
            "uuid": str(self.instance.id),
            "created": self.instance.created.isoformat(),
            "modified": self.instance.modified.isoformat(),
            "state_id": self.instance.state_id,
            "remote_id": self.instance.remote_id,
            "title": self.instance.title,
        })

    def link_to_sponsors(self):
        from capitolzen.proposals.managers import LegislatorManager
        query = """
        MATCH (bill:Bill {uuid: $bill_uuid}), 
            (legislator:Legislator {remote_id: $remote_id})
        MERGE (bill)<-[r:SPONSOR {
            type: $type
            human_weight: $human_weight
        }]-(legislator)
        RETURN bill, legislator
        """
        for sponsor in self.instance.sponsors:
            # Verify Legislator exists and is updated
            response = LegislatorManager(
                state=self.instance.state.capitalize()
            ).update(None, sponsor.get('leg_id'), None)

            if response:
                # Now that we know that they exist link them to the bill
                if sponsor.get('type') == "primary":
                    human_weight = 2
                else:
                    human_weight = 1
                self.graph.data(query, parameters={
                    "remote_id": sponsor.get('leg_id'),
                    "bill_uuid": str(self.instance.id),
                    "type": sponsor.get('type'),
                    "human_weight": human_weight
                })

    def _get_keyphrases(self):
        # Extract keywords and phrases from the current document so we know
        # what to search for in ES.
        r = Rake()
        r.extract_keywords_from_text(self.instance.content)
        key_phrases = [
            keyphrase[1] for keyphrase in r.get_ranked_phrases_with_scores()
            if keyphrase[0] >= self.min_rank_score
        ]
        if not key_phrases:
            key_phrases = [
                keyphrase[1]
                for keyphrase in
                r.get_ranked_phrases_with_scores()[:self.default_list_length]
            ]

        return key_phrases

    def _build_related_lists(self):
        # Build the list of related documents from ES based on the keywords /
        # phrases extracted from the current document we're analyzing
        if self.related_docs:
            return self.related_docs
        self.related_docs = {
            "ids": [],
            "content": []
        }
        for phrase in self._get_keyphrases():
            s = Search().using(
                self.es_client).query('match_phrase', content=phrase)
            s.doc_type(BillDocument)
            response = s.execute()
            self.related_docs['ids'] += list(
                set([hit.remote_id for hit in response]) -
                set(self.related_docs['ids'])
            )
            self.related_docs['content'] += list(
                set([hit.content for hit in response]) -
                set(self.related_docs['content'])
            )
        # Don't include the document itself in the analysis
        self.related_docs['ids'].remove(self.instance.remote_id)
        self.related_docs['content'].remove(self.instance.content)

        return self.related_docs

    def _generate_similarity_scores(self):
        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in self._build_related_lists()['content']]
        dictionary = corpora.Dictionary(gen_docs)
        corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
        tf_idf = models.TfidfModel(corpus)
        sims = similarities.Similarity(
            '/tmp/tst', tf_idf[corpus], num_features=len(dictionary)
        )
        query_doc = [w.lower() for w in word_tokenize(self.instance.content)]
        query_doc_bow = dictionary.doc2bow(query_doc)
        query_doc_tf_idf = tf_idf[query_doc_bow]
        return sims[query_doc_tf_idf]

    def create_similarity_relation(self):
        # Find words of most interest / value in bill
        # TODO: Might be able to simplify / improve results by using ES's
        # aggregation & significant_terms capabilities.

        for idx, score in enumerate(self._generate_similarity_scores()):
            query = """
            MATCH (bill:Bill {remote_id: $remote_id}),  
                (related_bill:Bill {remote_id: $related_id})
            CREATE (bill)-[r:SIMILAR_TO {
                content_similarity: $similarity_score
                }]->(related_bill)
            RETURN r
            """
            self.graph.data(query, parameters={
                "remote_id": self.instance.remote_id,
                "related_id": self._build_related_lists()['ids'][idx - 1],
                "similarity_score": score
            })

    def run(self):
        self.merge()
        self.link_to_sponsors()
        self.create_similarity_relation()


class LegislatorGraph(BasicGraph):
    instance_class = Legislator

    def merge(self):
        query = """
        MERGE (legislator:Legislator {uuid: $uuid})
        ON CREATE SET legislator.created = $created, 
            legislator.remote_id = $remote_id,
            legislator.state = $state,
            legislator.active = $active,
            legislator.chamber = $chamber,
            legislator.party = $party,
            legislator.district = $district,
            legislator.email = $email,
            legislator.first_name = $first_name,
            legislator.last_name = $last_name,
            legislator.updated_at = $updated_at,
            legislator.created_at = $created_at
        ON MATCH SET legislator.modified = $modified,
            legislator.active = $active,
            legislator.chamber = $chamber,
            legislator.party = $party,
            legislator.district = $district,
            legislator.email = $email,
            legislator.last_name = $last_name,
            legislator.updated_at = $updated_at
        RETURN legislator
        """
        self.graph.data(query, parameters={
            "uuid": str(self.instance.id),  # index
            "created": self.instance.created.isoformat(),
            "modified": self.instance.modified.isoformat(),
            "remote_id": self.instance.remote_id,  # index
            "state": self.instance.state,
            "active": self.instance.active,
            "chamber": self.instance.chamber,
            "party": self.instance.party,
            "district": self.instance.district,
            "email": self.instance.email,
            "first_name": self.instance.first_name,
            "last_name": self.instance.last_name,
            "updated_at": self.instance.updated_at.isoformat(),
            "created_at": self.instance.created_at.isoformat()
        })
