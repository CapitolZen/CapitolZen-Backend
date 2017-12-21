from json import dump, load

class MobileDoc(object):
    version: "0.3.1"
    markups: []
    atoms: []
    cards: []
    sections: []

    @property
    def json(self):
        data = {
            'version': self.version,
            'atoms': self.atom,
            'markups': self.markups,
            'cards': self.cards,
            'sections': self.sections
        }

        return dump(data)

    def add_p(self, text):
        wrapper = [
            1, 'p', [
                [0, [], 0, text]
            ]
        ]

        self.sections.append(wrapper)
