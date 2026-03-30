from dataclasses import dataclass


@dataclass
class Address:
    name: str
    street: str
    city: str
    postal_code: str
    country: str
