def normalize_phone_number(value: str) -> str:
    return "".join(char for char in value.strip() if char.isdigit() or char == "+")

