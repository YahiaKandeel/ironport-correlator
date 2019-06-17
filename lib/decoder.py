################################################################################
# Decoder, email subject & attachments
################################################################################
from email.header import decode_header


def decode(text):
    '''
        Decode any email encoded subjects' and attachments' names
    '''
    result = []
    blacklist = ['\r\n', '\\r\\n', '\\\r\\\n', '\\\\r\\\\n']

    parts = decode_header(text)
    # Iterate over the message parts
    for string, encoding in parts:
        try:
            if encoding:
                string = str(string, encoding)
                # decode to UTF-8
                string = string.encode().decode()
                result.append(string)
                print(string)

            # If there is no ecoding used:
            elif not encoding and type(string) != bytes:
                result.append(str(string))
                print(string)

        # If there is an exception, return the input as it is
        except Exception as error:
            print("ERROR -> ", text, error)
            return text

    # Construct Result
    result = ' '.join(result).strip()
    # Removing Bad Chars
    for badchrs in blacklist:
        result = result.replace(badchrs, '')

    return result
