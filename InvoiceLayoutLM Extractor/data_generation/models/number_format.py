from dataclasses import dataclass


@dataclass
class NumberFormat:
    """Controls how numbers and currency values are displayed."""
    decimal_separator: str      # "." or ","
    thousands_separator: str    # "," or "." or " " or ""
    currency_symbol: str        # "EUR", "€", "USD", "$", "GBP", "£", "CHF"
    currency_position: str      # "after" (123.45 EUR) or "before" ($ 123.45)

    def format_currency(self, value: float) -> str:
        """Format a float as a currency string."""
        formatted_number = self.format_number(value)
        if self.currency_position == "before":
            return f"{self.currency_symbol} {formatted_number}"
        return f"{formatted_number} {self.currency_symbol}"

    def format_number(self, value: float, decimals: int = 2) -> str:
        """Format a float with locale-appropriate separators."""
        # Split into integer and decimal parts
        abs_value = abs(value)
        int_part = int(abs_value)
        dec_part = round(abs_value - int_part, decimals)

        # Format decimal part
        dec_str = f"{dec_part:.{decimals}f}"[2:]  # remove "0."

        # Add thousands separators to integer part
        int_str = f"{int_part:,}".replace(",", "\x00")
        int_str = int_str.replace("\x00", self.thousands_separator)

        sign = "-" if value < 0 else ""
        return f"{sign}{int_str}{self.decimal_separator}{dec_str}"
