from dataclasses import dataclass, field

from models.address import Address
from models.line_item import LineItem
from models.number_format import NumberFormat
from models.payment_info import PaymentInfo
from models.style import Style


@dataclass
class Invoice:
    invoice_number: str
    invoice_date: str
    due_date: str
    seller: Address
    buyer: Address
    line_items: list[LineItem] = field(default_factory=list)
    currency: str = "EUR"
    locale: str = "en_US"
    style: Style | None = None
    number_format: NumberFormat | None = None
    payment_info: PaymentInfo | None = None

    @property
    def subtotal(self) -> float:
        return round(sum(item.line_total for item in self.line_items), 2)

    @property
    def total_tax(self) -> float:
        return round(sum(item.tax_amount for item in self.line_items), 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.total_tax, 2)
