
# symbols_keys = [
#     '<<=', '>>=', '++', '--', '==', '<<', '>>', '&&', '||', '->', '::', '+=', '##', 
#     '-=', '*=', '/=','^=', '|=', '%=', '&=', '~=', '//', '+', '-', '*', '/', '%', '^', 
#     '|', '&', '~', ',', '<', '>', '(', ')', '!', '.', '?', ':', '{', '}', '[', ']', '\\', ';', '"', '\'', '=', '#', ' ', '\n', '\t'
# ]

_symbols_keys = {
    "ls_assignment": '<<=', 
    "rs_assignment": '>>=', 
    "increment": '++', 
    "decrement": '--', 
    "logical_equal": '==', 
    "ls": '<<', 
    "rs": '>>', 
    "logical_and": '&&', 
    "logical_or": '||', 
    "ptr_member_access": '->', 
    "namespace_member_access": '::', 
    "add_assignment": '+=', 
    "token_concatinate": '##', 
    "sub_assignment": '-=', 
    "mul_assignment": '*=',
    "div_assignment": '/=',
    "xor_assignment": '^=', 
    "or_assignment": '|=', 
    "mod_assignment": '%=', 
    "and_assignment": '&=', 
    "tilda_assignment": '~=', 
    "single_ln_comment": '//', 
    "add": '+', 
    "sub": '-', 
    "mul": '*', 
    "div": '/', 
    "mod": '%', 
    "xor": '^', 
    "or": '|', 
    "and": '&', 
    "tilda": '~', 
    "comma": ',', 
    "less_than": '<', 
    "greater_than": '>', 
    "open-pareph": '(', 
    "close-pareph": ')', 
    "not": '!', 
    "member_access": '.', 
    "ternnary": '?', 
    "var_type_declar": ':', 
    "open_scope": '{', 
    "close_scope": '}', 
    "open_list": '[', 
    "close_list": ']', 
    "line-concatinate": '\\', 
    "end-of-line": ';', 
    "str_quote": '"', 
    "char_quote": '\'', 
    "assignment": '=', 
    "token_as_str": '#', 
    "white_space1": ' ', 
    "white_space2": '\n', 
    "white_space3": '\t'
}

symbols_keys = list(_symbols_keys.values())
key_words = [
    "char",
    "short",
    "int",
    "long",
    "float",
    "double",
    "string",
    "void",
    "auto",
    "fn",
    "struct",
    "func",
    "sizeof",
    "c8",
    "i16",
    "i32",
    "i64",
    "f32",
    "f64",
    "vec2",
    "vec3",
    "vec4",
    "mat2x2",
    "mat3x3",
    "mat4x4",
    "var",
    "typeof",
    "if",
    "for",
    "while",
    "loop",
    "do",
    "switch",
    "case",
    "foreach",
    "true",
    "false"
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

def str_get_scope_end(text: str, openDel: str, closeDel: str, offset: int) -> int:
    depth = 0

    for i in range(offset, len(text), 0):
        if text.startswith(openDel, i):
            depth += 1
            i += len(openDel)
        elif text.startswith(closeDel, i):
            depth -= 1

            if depth == 0:
                return i
            
            i += len(closeDel)
        else:
            i += 1
    
    return -1

def list_get_scope_end(lst: list, openDel: str, closeDel: str, offset: int) -> int:
    depth = 0

    for i in range(offset, len(lst)):
        if lst[i] == openDel:
            depth += 1
        elif lst[i] == closeDel:
            depth -= 1

            if depth == 0:
                return i
    
    return -1

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

        if text.startswith("//", i) or text.startswith("#", i):
            end = scan_for(text, "\n", i)

            if end == -1:
                end = len(text) - 1

            if lastToken:
                tokens.append(lastToken)
                lastToken = ""

            tokens.append(text[i:end])
            i = end + 1
            continue

        if text.startswith("/*", i):
            end = scan_for(text, "*/", i)

            if end == -1:
                end = len(text) - 1

            if lastToken:
                tokens.append(lastToken)
                lastToken = ""

            tokens.append(text[i:end + 2])
            i = end + 2
            continue

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

def section_token_list(tokenList: list[str]) -> list[str]:
    scopes = [
        { "open": "{", "close": "}" },
        { "open": "(", "close": ")" },
        { "open": "[", "close": "]" }
    ]
    newList = []
    i = 0

    while i < len(tokenList):
        stop = False

        for scope in scopes:
            if tokenList[i] == scope["open"]:
                end = list_get_scope_end(tokenList, scope["open"], scope["close"], i)

                if end == -1:
                    raise Exception(f"Error: Misting {scope["close"]} detected")
                
                newToken = ""

                for j in range(i, end + 1):
                    newToken += tokenList[j] + " "

                newList.append(newToken[:-1])
                i = end + 1
                stop = True
                break

        if stop:
            continue

        newList.append(tokenList[i])
        i += 1

    return newList

class Token:
    def __init__(self, tokenType: str, value):
        self.tokenType = tokenType
        self.value = value

    def __str__(self):
        return f"{self.tokenType}: {str(self.value)}"

def create_token(token: str) -> Token:
    if token in symbols_keys:
        return Token(list(_symbols_keys.keys())[list(symbols_keys).index(token)], token)
    else:
        if token in key_words:
            return Token("keyword", token)
        elif is_key_word(token):
            return Token("word", token)
        elif is_number(token):
            return Token("number", token)
        elif token.startswith("#"):
            return Token("pre-processor", token)
        elif token.startswith("{"):
            return Token("scope-body", token)
        elif token.startswith("("):
            return Token("expr-body", token)
        elif token.startswith("["):
            return Token("list-body", token)
        else:
            return Token("unknown", token)

def label_tokens(tokens: list[str]) -> list[Token]:
    newList = []
    localList = []
    lastScope = ""
    
    for token in tokens:
        if token in ["{", "(", "["]:
            if token == "{":
                localList.append(Token("scope-body", []))
            elif token == "(":
                localList.append(Token("expr-body", []))
            elif token == "[":
                localList.append(Token("list-body", []))

            continue

        if token in ["}", ")", "]"]:
            lst = localList.pop(len(localList) - 1)

            if localList:
                localList[-1].value.append(lst)
            else:
                newList.append(lst)

            continue

        if localList:
            localList[-1].value.append(create_token(token))
        else:
            newList.append(create_token(token))

    return newList

def line_print(value):
    print(value, end = "")

def print_body_tokens(tokens: list[Token], scope = 0):
    for i in range(len(tokens)):
        token = tokens[i]

        if token.tokenType == "scope-body":
            print()
            print("{")
            line_print("    " * (scope + 1))
            print_body_tokens(token.value, scope + 1)
            line_print("}")

            if i + 1 < len(tokens) and tokens[i + 1].value != ";":
                print()

        elif token.tokenType == "expr-body":
            line_print("(")
            print_body_tokens(token.value, scope)
            line_print(")")
        elif token.tokenType == "list-body":
            print("[")
            print_body_tokens(token.value, scope)
            print("]")
        else:
            if i > 0 and is_key_word(token.value) and is_key_word(tokens[i - 1].value):
                line_print(" ")
                
            line_print(token.value)

            if token.value[0] == "#":
                print()

            if token.value == ";":
                print()

                if i + 1 < len(tokens) and tokens[i + 1].value != "}":
                    line_print("    " * scope)

                if i - 1 >= 0 and tokens[i - 1].value == "}":
                    print()

def print_tokens(tokens: list[Token], scope = 0, single_line = False):
    for i in range(len(tokens)):
        token = tokens[i]

        if type(token.value) == list:
            if token.tokenType == "scope-body":
                print()
                line_print("    " * scope)
                print("{")
                line_print("    " * (scope + 1))
                print_tokens(token.value, scope + 1)
                print()
                line_print("    " * scope)
                line_print("}")
                
                if i + 1 < len(tokens) and tokens[i + 1].value != ";":
                    print()

                line_print("    " * scope)
            elif token.tokenType == "expr-body":
                line_print("(")
                print_tokens(token.value, single_line = True)
                line_print(")")
            elif token.tokenType == "list-body":
                line_print("[")
                print_tokens(token.value, single_line = True)
                line_print("]")
        elif type(token.value) == str:
            if i > 0 and type(tokens[i - 1].value) == str:
                if tokens[i - 1].value in [":", ","] or (is_key_word(tokens[i - 1].value) and is_key_word(token.value)):
                    line_print(" ")
                
            line_print(token.value)

            if token.value.startswith("#"):
                print()

            if token.value == ";" and i + 1 < len(tokens) and tokens[i + 1] != "}" and not single_line:
                print()
                
                if i + 1 < len(tokens) and tokens[i + 1].value != "}":
                    line_print("    " * scope)

if __name__ == "__main__":
    print(is_number("100.24"))
    # 10+20*3^2%3/2*t = 2, 9 + 1<2 && 2 > 3 + 2 << 2==2 if int()
    # with open("codeTest.txt", "r") as file:
    #     text = file.read()
    #     tokens = section_token_list(tokenize(text))
    #     
    #     for token in tokens:
    #         print(token)

    text = "10 + 5 * 5 / 2"
    tokens = label_tokens((tokenize(text)))
    operator_stack = []
    operand_stack = []

    for token in tokens:
        print(str(token))

    # print_tokens(tokens)
    exit()

    with open("codeTest.txt", "r") as file:
        text = file.read()
        tokens = label_tokens((tokenize(text)))

        print_tokens(tokens)
        # print_body_tokens(tokens)

    # print(tokenize("game.get(); +     i++ 1.0f + 10+20*3^2%3/2*t = 2, 9 + 1<2 && 2 > 3 + 2 << 2==2 if int()>>=0\"Hello, World!\"\"Hello, World!\" + i++"))