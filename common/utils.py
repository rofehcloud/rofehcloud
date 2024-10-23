from common.logger import log_message


def generate_collection_name(profile: str) -> str:
    collection_name = f"c_{profile}"
    return collection_name


def fix_unclosed_quote(line):
    # Count the number of double quotes in the line
    quote_count = line.count('"')
    # If the count is odd, add a closing quote
    if quote_count % 2 != 0:
        line += '"'
        log_message("DEBUG", f"Added a closing quote to the line: {line}")
    return line
