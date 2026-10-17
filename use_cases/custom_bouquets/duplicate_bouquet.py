from use_cases.custom_bouquets.get_bouquet import get_bouquet
from use_cases.custom_bouquets.configuration_input import configuration_input
from use_cases.custom_bouquets.create_bouquet import create_bouquet

def duplicate_bouquet(db,actor,identity):
    original=get_bouquet(db,identity,lock=True)
    data=configuration_input(original)
    return create_bouquet(db,actor,data,duplicated_from=original.id)
