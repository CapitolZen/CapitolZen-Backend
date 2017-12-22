

class MobileDoc(object):

    def __init__(self):
        self.version = "0.3.1"
        self.markups = []
        self.atoms = []
        self.cards = []
        self.sections = []

    @property
    def data(self):
        data = {
            'version': self.version,
            'atoms': self.atoms,
            'markups': self.markups,
            'cards': self.cards,
            'sections': self.sections
        }
        return data

    def add_p(self, text):
        wrapper = [
            1, 'p', [
                [0, [], 0, text]
            ]
        ]
        self.sections.append(wrapper)
