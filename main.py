
symbols_keys = [
    '<<=', '>>=', '++', '--', '==', '<<', '>>', '&&', '||', '->', '::', '+=', 
    '-=', '*=', '/=','^=', '|=', '%=', '&=', '~=', '//', '+', '-', '*', '/', '%', '^', 
    '|', '&', '~', ',', '<', '>', '(', ')', '!', '.', '?', ':', '{', '}', '[', ']', '\\', ';', '"', '\'', '=', '#', ' ', '\n', '\t'
]

def get_starts_with(text, symbol, offset = 0) -> str:
    if text.startswith(symbol, offset):
        return text[offset:offset+ len(symbol)]
    
    return ""

def scan_for(text, symbol, offset) -> int:
    for i in range(offset, len(text)):
        if text.startswith(symbol, i):
            return i
        
    return -1

def find_string_end(text: str, symbol, offset) -> int:
    i = offset
    
    while i < len(text):
        if text.startswith("\\\\", i):
            print("TEST! TEST!")
            i += 2
            continue
        elif text.startswith("\\" + symbol, i):
            print(f"from {offset} to {i}")
            i += 1 + len(symbol)
            continue

        if text.startswith(symbol, i):
            return i
        
        i += 1
        
    return -1

def is_whitespace(token) -> bool:
    if token in [' ', '\n', '\t']:
        return True
    
    return False

def is_number(token) -> bool:
    for i in range(len(token)):
        if not (ord(token[i]) in range(ord('0'), ord('9') + 1) 
                or token[i] in "-."
                or (ord(token[i].lower()) in range(ord('a'), ord('z') + 1) and i == len(token) - 1)):
            return False
        
    return True

def is_key_word(token) -> bool:
    if not token:
        return False
    
    if ord(token[0]) in range(ord('0'), ord('9') + 1):
        return False
    
    for symbol in symbols_keys:
        if symbol in token:
            return False
        
    return True

def tokenize(text) -> list[str]:
    tokens = []
    lastToken = ""
    i = 0

    while i < len(text):
        if text[i] == '"' or text[i] == "'":
            end = find_string_end(text, text[i], i + 1)

            if end != -1:
                if lastToken:
                    tokens.append(lastToken)
                    lastToken = ""

                tokens.append(text[i:end + 1])
                i = end + 1
                continue
            else:
                print(f"\"{text[i:]}\"")
                raise Exception(f"Forgot closing token for '{text[i]}' at index {i}")

        skip = False

        for symbol in symbols_keys:
            startToken = get_starts_with(text, symbol, i)

            if startToken == "\"":
                print("INVALID-TOKEN: '\"'")

            if startToken:
                if lastToken:
                    if is_number(lastToken) and startToken == '.':
                        continue

                    tokens.append(lastToken)
                    lastToken = ""

                if not is_whitespace(startToken):
                    tokens.append(startToken)

                i += len(startToken)
                skip = True
                break

        if skip:
            continue

        if not is_whitespace(text[i]):
            lastToken += text[i]

        i += 1

    if lastToken:
        tokens.append(lastToken)
        lastToken = ""

    return tokens

if __name__ == "__main__":
    print(is_number("100.24"))
    # 10+20*3^2%3/2*t = 2, 9 + 1<2 && 2 > 3 + 2 << 2==2 if int()
    with open("testMoreCode.txt", "r") as file:
        text = file.read()
        tokens = tokenize(text)
        print(tokens)

    # print(tokenize("game.get(); +     i++ 1.0f + 10+20*3^2%3/2*t = 2, 9 + 1<2 && 2 > 3 + 2 << 2==2 if int()>>=0\"Hello, World!\"\"Hello, World!\" + i++"))