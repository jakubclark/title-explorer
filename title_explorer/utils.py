from uuid import UUID, uuid3

TITLE_NAMESPACE = UUID('12345678123456781234567812345678')


def to_internal_id(external_id: str) -> str:
    return uuid3(TITLE_NAMESPACE, external_id).hex
