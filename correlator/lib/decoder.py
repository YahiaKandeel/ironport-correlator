from email.header import decode_header


def decode(text):
    blacklist = ['\r\n', '\\r\\n', '\\\r\\\n', '\\\\r\\\\n']
    items = decode_header(text)
    result = []

    # ITerating Over Items
    for string, encoding in items:
        try:
            if encoding:
                string = str(string, encoding).encode().decode()
                # print('\r\n---------------', string, encoding,'--------------')
                result.append(string)
            elif not encoding and type(string) != bytes:
                # print('\r\n####################', string, encoding,'####################')
                result.append(str(string))
        except Exception as e:
            print("\r\n\ISUSEEEEE-------->", text, str(e),'--------------\r\n\r\n')
            result = [text]

    # Construct Result, Removing Bad Chars
    result = ' '.join(result).strip()
    for badchrs in blacklist:
        result = result.replace(badchrs,'')

    if result:
        print('\r\n\r\n####################', result, '####################')

    return result
