from email.header import decode_header
import codecs


def decode(text):
    result = []
    items = decode_header(text)
    for string, encoding in items:
        if encoding:
            result.append(codecs.decode(string, encoding))
        elif not encoding and type(string) != bytes:
            result.append(str(string))
    return ''.join(result)
