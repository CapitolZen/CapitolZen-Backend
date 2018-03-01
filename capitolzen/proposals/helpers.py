import re
from capitolzen.proposals.models import Bill


class InputDataParser(object):
    """
    Eh.
    """

    input = ""
    bill_search_list = []

    def __init__(self, input):
        self.input = input

    def add_to_search(self, additions):
        if not additions:
            return

        self.bill_search_list.extend(additions)

    def reduce(self, results):
        if not results:
            return

        stopwords = results
        querywords = self.input.split()
        resultwords = [word for word in querywords if word.lower() not in stopwords]
        self.input = ' '.join(resultwords)

    def clean(self):
        """
        Clean the input data...
        :return:
        """

        #
        # Lot of parsing effort... Dates usually have numbers in them and you can format them in a million
        # https://www.regextester.com/6
        dates = "((0?[13578]|10|12)(-|\/)(([1-9])|(0[1-9])|([12])([0-9]?)|(3[01]?))(-|\/)((19)([2-9])(\d{1})|(20)([01])(\d{1})|([8901])(\d{1}))|(0?[2469]|11)(-|\/)(([1-9])|(0[1-9])|([12])([0-9]?)|(3[0]?))(-|\/)((19)([2-9])(\d{1})|(20)([01])(\d{1})|([8901])(\d{1})))"
        results = re.findall(dates, self.input)
        if results:
            dates = []
            for result in results:
                dates.append(result[0])
            self.reduce(dates)

    def search_for_hrs(self):
        results = re.findall('HR [0-9]+', self.input)
        self.add_to_search(results)
        self.reduce(results)

    def search_for_hjrs(self):
        results = re.findall('HJR [A-Z]', self.input)
        self.add_to_search(results)
        self.reduce(results)

    def search_for_hcrs(self):
        results = re.findall('HCR [1-9]', self.input)
        self.add_to_search(results)
        self.reduce(results)

    def search_for_table_scraps(self):
        """
        All the obvious data has been removed at this point, so now we parse out the remaining ints and do some work
        :return:
        """
        raw = results = re.findall('[0-9]+', self.input)
        for i, item in enumerate(results):

            # remove leading 0s.
            item = item.lstrip('0')

            if not item:
                continue

            # convert to int for math
            item = int(item)

            # do some shoddy michigan specific bill extraction concepts
            if item > 4000:
                item = "HB %s" % item
            else:
                item = "SB %s" % item

            results[i] = item

        self.add_to_search(results)
        self.reduce(raw)

    def validate_bill_list(self):
        bill_search_list = list(set(self.bill_search_list))
        bills = Bill.objects.filter(state_id__in=bill_search_list).values_list('state_id', flat=True)
        return bills

    def get(self):

        if not self.input:
            return []

        self.clean()

        self.search_for_hjrs()
        self.search_for_hcrs()
        self.search_for_hrs()
        self.search_for_table_scraps()
        return self.validate_bill_list()


