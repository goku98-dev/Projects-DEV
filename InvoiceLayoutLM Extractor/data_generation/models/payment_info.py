from dataclasses import dataclass


@dataclass
class PaymentInfo:
    bank_name: str
    iban: str
    bic: str
    payment_terms: str
