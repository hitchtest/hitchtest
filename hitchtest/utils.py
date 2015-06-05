
def to_camel_case(text):
    return ''.join(x for x in text.title() if x.isalpha() or x.isdigit())

def to_underscore_style(text):
    text = text.lower().replace(" ", "_").replace("-", "_")
    return ''.join(x for x in text if x.isalpha() or x.isdigit() or x == "_")
