from dataclasses import dataclass


@dataclass
class LineItem:
    position: int
    description: str
    quantity: int
    unit_price: float
    tax_rate: float
    article_number: str | None = None

    @property
    def line_total(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    @property
    def tax_amount(self) -> float:
        return round(self.line_total * self.tax_rate, 2)
