
symbols_keys = [
    '<<=', '>>=', '++', '--', '==', '<<', '>>', '&&', '||', '->', '::', '+=', 
    '-=', '*=', '/=','^=', '|=', '%=', '&=', '~=', '+', '-', '*', '/', '%', '^', 
    '|', '~', ',', '<', '>', '(', ')', '!', '.', '?', ':', '{', '}', '[', ']', '\\', ';', '"', '\'', '=', ' '
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
            end = scan_for(text, text[i], i + 1)

            if end != -1:
                if lastToken:
                    tokens.append(lastToken)
                    lastToken = ""

                tokens.append(text[i:end + 1])
                i = end + 1
                continue
            else:
                raise Exception(f"Forgot closing token for '{text[i]}' at index {i}")
            
        skip = False

        for symbol in symbols_keys:
            startToken = get_starts_with(text, symbol, i)

            if startToken:
                if lastToken:
                    if is_number(lastToken) and startToken == '.':
                        break

                    tokens.append(lastToken)
                    lastToken = ""

                if startToken != ' ':
                    tokens.append(startToken)

                i += len(startToken)
                skip = True

        if skip:
            continue

        if text[i] != ' ':
            lastToken += text[i]

        i += 1

    if lastToken:
        tokens.append(lastToken)
        lastToken = ""

    return tokens

if __name__ == "__main__":
    print(is_number("100.24"))
    # 10+20*3^2%3/2*t = 2, 9 + 1<2 && 2 > 3 + 2 << 2==2 if int()
    print(get_starts_with("1<<1", "<<", 1))
    print(tokenize("game.get() + i++ 1.0f + 10+20*3^2%3/2*t = 2, 9 + 1<2 && 2 > 3 + 2 << 2==2 if int()>>=0\"Hello, World!\"\"Hello, World!\" + i++"))