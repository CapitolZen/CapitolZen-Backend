from collections import namedtuple

AvailableStateChoices = (
    ('MI', 'Michigan'),
    ('OH', "Ohio")
)

StateData = namedtuple('StateData',
                       'name title lower_bill_prefix upper_bill_prefix lower_chamber upper_chamber is_active'
                       )

mi = StateData(
    name='MI',
    title="Michigan",
    lower_bill_prefix='HB',
    upper_bill_prefix='SB',
    lower_chamber='House',
    upper_chamber='Senate',
    is_active=True
)

AVAILABLE_STATES = [mi]

# {
#     "id": "MI",
#     "title": "Michigan",
#     "lower_bill_prefix": "HB",
#     "upper_bill_prefix": "SB",
#     "lower_bill_start": "4001",
#     "upper_bill_start": "0001",
#     "is_active": True
# }



