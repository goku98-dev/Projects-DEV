"""Generates random invoice data using Faker."""

import random
from datetime import timedelta

from faker import Faker

from models.address import Address
from models.line_item import LineItem
from models.invoice import Invoice
from models.number_format import NumberFormat
from models.payment_info import PaymentInfo
from models.style import Style


PRODUCT_NAMES: list[str] = [
    # Office furniture
    "Office Chair", "Standing Desk", "Ergonomic Desk Chair", "Conference Table",
    "Filing Cabinet 3-Drawer", "Bookshelf 5-Tier", "Desk Organizer",
    "Monitor Arm Mount", "Laptop Stand", "Footrest Ergonomic",
    "Room Divider Panel", "Coat Rack", "Desk Pad Leather",
    # Electronics & IT
    "Monitor 27\"", "Wireless Keyboard", "USB-C Hub", "Webcam HD",
    "Noise-Cancelling Headphones", "External SSD 1TB", "Ethernet Cable 5m",
    "Document Scanner", "Ergonomic Mouse", "Webcam Light Ring",
    "HDMI Cable 2m", "Power Strip with USB", "Wireless Presenter",
    "Docking Station USB-C", "Graphics Card RTX 4060", "RAM Module 16GB DDR5",
    "Mechanical Keyboard RGB", "Bluetooth Speaker Portable", "UPS Battery Backup 1500VA",
    "Network Switch 8-Port", "Wireless Access Point", "Thunderbolt Cable 1m",
    "DisplayPort Cable 3m", "External HDD 4TB", "NVMe SSD 2TB",
    "Laptop Charger Universal 65W", "Screen Privacy Filter 24\"",
    "Surge Protector 6-Outlet",
    # Office supplies
    "Printer Paper A4 (500 sheets)", "Ballpoint Pens (12-pack)",
    "Whiteboard Marker Set", "Desk Lamp LED", "Mouse Pad XL",
    "Cable Management Kit", "Toner Cartridge Black", "Notebook A5 Ruled",
    "Sticky Notes Assorted", "Binder Clips Assorted (48-pack)",
    "Laminating Pouches A4 (100-pack)", "Label Maker Tape 12mm",
    "Paper Shredder Cross-Cut", "Stapler Heavy-Duty", "Scissors 8\" Stainless",
    "Envelope C4 (50-pack)", "Correction Tape 6-pack", "Highlighter Set (5 colors)",
    "Clipboard A4", "Desk Calendar 2026",
    # Cleaning & maintenance
    "Screen Cleaning Kit", "Compressed Air Duster (6-pack)",
    "Microfiber Cloth Set (10-pack)", "Hand Sanitizer 500ml",
    "Disinfecting Wipes (75-pack)",
    # Services (multi-word for variety)
    "Annual Software License Renewal", "IT Support Service (1 hour)",
    "Printer Maintenance Contract (quarterly)",
    "Office Equipment Installation Service",
    "Data Backup Service (monthly subscription)",
    "Managed Firewall Service (annual)",
    "Cloud Storage Plan 1TB (yearly)",
    "Professional Monitor Calibration",
]

TAX_RATES: list[float] = [0.0, 0.07, 0.19]

FONT_FAMILIES: list[str] = [
    "Arial, Helvetica, sans-serif",
    "Georgia, 'Times New Roman', serif",
    "'Courier New', Courier, monospace",
    "Verdana, Geneva, sans-serif",
    "'Trebuchet MS', sans-serif",
    "Tahoma, Geneva, sans-serif",
    "'Lucida Sans', 'Lucida Grande', sans-serif",
    "'Palatino Linotype', 'Book Antiqua', Palatino, serif",
]

HEADER_COLORS: list[str] = [
    "#2c3e50", "#1a5276", "#0e6655", "#6c3483",
    "#1c2833", "#4a4a4a", "#2e4053", "#1b4f72",
    "#7b241c", "#1e8449", "#2874a6", "#6e2c00",
    "#283747", "#0b5345", "#4a235a", "#7e5109",
]

BORDER_STYLES: list[str] = ["solid", "none", "dotted"]

# Locale configurations: (locale, date_format, currency, tax_rates)
LOCALE_CONFIGS: list[dict] = [
    {"locale": "de_DE", "date_format": "%d.%m.%Y", "currency": "EUR",
     "tax_rates": [0.0, 0.07, 0.19]},
    {"locale": "en_US", "date_format": "%m/%d/%Y", "currency": "USD",
     "tax_rates": [0.0, 0.06, 0.0825, 0.10]},
    {"locale": "en_GB", "date_format": "%d/%m/%Y", "currency": "GBP",
     "tax_rates": [0.0, 0.05, 0.20]},
    {"locale": "fr_FR", "date_format": "%d/%m/%Y", "currency": "EUR",
     "tax_rates": [0.0, 0.055, 0.10, 0.20]},
    {"locale": "de_CH", "date_format": "%d.%m.%Y", "currency": "CHF",
     "tax_rates": [0.0, 0.025, 0.081]},
    {"locale": "de_AT", "date_format": "%d.%m.%Y", "currency": "EUR",
     "tax_rates": [0.0, 0.10, 0.20]},
]

# Number format presets per currency
NUMBER_FORMATS: dict[str, list[NumberFormat]] = {
    "EUR": [
        NumberFormat(decimal_separator=",", thousands_separator=".", currency_symbol="EUR", currency_position="after"),
        NumberFormat(decimal_separator=",", thousands_separator=".", currency_symbol="€", currency_position="after"),
        NumberFormat(decimal_separator=",", thousands_separator=" ", currency_symbol="€", currency_position="before"),
        NumberFormat(decimal_separator=".", thousands_separator=",", currency_symbol="EUR", currency_position="after"),
    ],
    "USD": [
        NumberFormat(decimal_separator=".", thousands_separator=",", currency_symbol="$", currency_position="before"),
        NumberFormat(decimal_separator=".", thousands_separator=",", currency_symbol="USD", currency_position="after"),
    ],
    "GBP": [
        NumberFormat(decimal_separator=".", thousands_separator=",", currency_symbol="£", currency_position="before"),
        NumberFormat(decimal_separator=".", thousands_separator=",", currency_symbol="GBP", currency_position="after"),
    ],
    "CHF": [
        NumberFormat(decimal_separator=".", thousands_separator="'", currency_symbol="CHF", currency_position="after"),
        NumberFormat(decimal_separator=".", thousands_separator="'", currency_symbol="CHF", currency_position="before"),
    ],
}


def generate_address(fake: Faker) -> Address:
    return Address(
        name=fake.company(),
        street=fake.street_address(),
        city=fake.city(),
        postal_code=fake.postcode(),
        country=fake.current_country(),
    )


def _generate_article_number() -> str:
    """Generate a realistic ERP-style article number."""
    formats: list[str] = [
        f"ART-{random.randint(10000, 99999)}",
        f"{random.randint(1000, 9999)}.{random.randint(100, 999)}",
        f"{random.choice(['A', 'B', 'C', 'P', 'M'])}{random.randint(10000, 99999)}",
        f"{random.randint(100000, 999999)}",
    ]
    return random.choice(formats)


def generate_line_items(num_items: int, include_article_numbers: bool = True,
                        tax_rates: list[float] | None = None) -> list[LineItem]:
    if tax_rates is None:
        tax_rates = TAX_RATES
    descriptions = random.sample(PRODUCT_NAMES, min(num_items, len(PRODUCT_NAMES)))
    items: list[LineItem] = []
    for i, desc in enumerate(descriptions, start=1):
        items.append(LineItem(
            position=i,
            description=desc,
            quantity=random.randint(1, 50),
            unit_price=round(random.uniform(1.50, 500.00), 2),
            tax_rate=random.choice(tax_rates),
            article_number=_generate_article_number() if include_article_numbers else None,
        ))
    return items


BANK_NAMES: list[str] = [
    "Deutsche Bank AG", "Commerzbank AG", "Sparkasse", "Volksbank",
    "UniCredit Bank", "ING-DiBa", "Postbank", "DZ Bank",
    "Crédit Agricole", "BNP Paribas", "Société Générale",
    "Barclays", "HSBC", "Lloyds Bank", "NatWest",
    "JPMorgan Chase", "Bank of America", "Wells Fargo", "Citibank",
    "UBS", "Credit Suisse", "Zürcher Kantonalbank", "Raiffeisen Schweiz",
]

PAYMENT_TERMS: list[str] = [
    "Please remit payment within the stated due date.",
    "Payment due upon receipt.",
    "Net 30 days from invoice date.",
    "Net 14 days. 2% discount for payment within 7 days.",
    "Payment due within 30 days. Late payments subject to 1.5% monthly interest.",
    "Please transfer the total amount by the due date.",
    "Payable within 60 days of invoice date.",
    "Immediate payment required.",
    "Please pay within 14 days of receipt.",
    "30 days net. Skonto 2% within 10 days.",
]


def _generate_iban(fake: Faker) -> str:
    """Generate a realistic-looking IBAN."""
    country = fake.current_country_code()
    check_digits = f"{random.randint(10, 99)}"
    # Generate bank-specific part (varying length by country style)
    bank_part = " ".join(
        f"{random.randint(1000, 9999)}" for _ in range(random.choice([4, 5, 6]))
    )
    return f"{country}{check_digits} {bank_part}"


def _generate_bic() -> str:
    """Generate a realistic-looking BIC/SWIFT code."""
    bank_code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
    country = random.choice(["DE", "FR", "GB", "US", "CH", "AT"])
    location = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=2))
    branch = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))
    return f"{bank_code}{country}{location}{branch}"


def generate_payment_info(fake: Faker) -> PaymentInfo:
    return PaymentInfo(
        bank_name=random.choice(BANK_NAMES),
        iban=_generate_iban(fake),
        bic=_generate_bic(),
        payment_terms=random.choice(PAYMENT_TERMS),
    )


def generate_style() -> Style:
    header_bg = random.choice(HEADER_COLORS)
    return Style(
        font_family=random.choice(FONT_FAMILIES),
        font_size_pt=random.choice([9, 10, 11, 12]),
        header_bg_color=header_bg,
        header_text_color="#ffffff",
        border_color=random.choice(["#cccccc", "#999999", "#dddddd", header_bg]),
        row_alt_bg_color=random.choice(["#f9f9f9", "#f2f2f2", "#eef2f7", "#ffffff"]),
        table_border_style=random.choice(BORDER_STYLES),
    )


def generate_invoice(locale: str = "de_DE", seed: int | None = None) -> Invoice:
    """Generate a single random invoice.

    If locale is "random", a locale is chosen randomly from LOCALE_CONFIGS.
    """
    if seed is not None:
        random.seed(seed)

    # Pick locale config
    if locale == "random":
        config = random.choice(LOCALE_CONFIGS)
    else:
        config = next((c for c in LOCALE_CONFIGS if c["locale"] == locale), LOCALE_CONFIGS[0])

    fake = Faker(config["locale"])
    if seed is not None:
        Faker.seed(seed)

    invoice_date = fake.date_between(start_date="-2y", end_date="today")
    due_date = invoice_date + timedelta(days=random.choice([14, 30, 45, 60]))

    num_items = random.randint(3, 8)
    currency: str = config["currency"]
    number_format = random.choice(NUMBER_FORMATS[currency])

    return Invoice(
        invoice_number=f"INV-{fake.unique.random_number(digits=6, fix_len=True)}",
        invoice_date=invoice_date.strftime(config["date_format"]),
        due_date=due_date.strftime(config["date_format"]),
        seller=generate_address(fake),
        buyer=generate_address(fake),
        line_items=generate_line_items(
            num_items,
            include_article_numbers=random.random() > 0.3,
            tax_rates=config["tax_rates"],
        ),
        currency=currency,
        locale=config["locale"],
        style=generate_style(),
        number_format=number_format,
        payment_info=generate_payment_info(fake),
    )
