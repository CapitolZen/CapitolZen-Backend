from py2neo import Graph
from django.conf import settings

from capitolzen.proposals.models import Bill, Legislator


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

    def merge(self):
        query = """
            MERGE (bill:Bill {uuid: $uuid})
            ON CREATE SET bill.summary = $summary, bill.created = $created, 
                bill.modified = $modified, bill.state_id = $state_id, 
                bill.remote_id = $remote_id, bill.title = $title
                bill.raw_text = $raw_text
            ON MATCH SET bill.modified = $modified, bill.summary = $summary,
                bill.title = $title, $bill.raw_text = $raw_text 
            RETURN bill
            """
        self.graph.data(query, parameters={
            "uuid": self.instance.id,
            "summary": self.instance.summary,
            "created": self.instance.created,
            "modified": self.instance.modified,
            "state_id": self.instance.state_id,
            "remote_id": self.instance.remote_id,
            "title": self.instance.title,
            "raw_text": self.instance.bill_raw_text
        })

    def link_to_sponsors(self):
        from capitolzen.proposals.managers import LegislatorManager
        query = """
        MATCH (bill:Bill {uuid: $bill_uuid}), 
            (legislator:Legislator {remote_id: $remote_id})
        MERGE (bill)<-[r:SPONSOR {type: $type}]-(legislator)
        RETURN bill, legislator
        """
        for sponsor in self.instance.sponsors:
            # Verify Legislator exists and is updated
            response = LegislatorManager(
                state=self.instance.state.capitalize()
            ).update(None, sponsor.get('leg_id'), None)

            if response:
                # Now that we know that they exist link them to the bill
                self.graph.data(query, parameters={
                    "remote_id": sponsor.get('leg_id'),
                    "bill_uuid": self.instance.id,
                    "type": sponsor.get('type')
                })

    def run(self):
        self.merge()
        self.link_to_sponsors()


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
            "uuid": self.instance.id,  # index
            "created": self.instance.created,
            "modified": self.instance.modified,
            "remote_id": self.instance.remote_id,  # index
            "state": self.instance.state,
            "active": self.instance.active,
            "chamber": self.instance.chamber,
            "party": self.instance.party,
            "district": self.instance.district,
            "email": self.instance.email,
            "first_name": self.instance.first_name,
            "last_name": self.instance.last_name,
            "updated_at": self.instance.updated_at,
            "created_at": self.instance.created_at
        })
