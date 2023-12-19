from database.models import DeliveryPlace


def old_place_view(place: DeliveryPlace) -> str:
    return f'Действующее место доставки: <b>{place.name}</b>'
