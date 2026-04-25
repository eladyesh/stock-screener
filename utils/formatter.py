def format_price(value):
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def color_change(value):
    if value is None:
        return "black"
    return "green" if value >= 0 else "red"