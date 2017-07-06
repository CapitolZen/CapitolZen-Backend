from json import dumps
from capitolzen.proposals.models import Wrapper, Bill


class ReportDocumentManager:
    def __init__(self, report):
        self.report = report

    DEFAULT = 'list'
    TABLE = 'table'

    def export(self):
        return dumps({})

    def output_by_format(self, file_type="docx"):
        return 'asdf'

