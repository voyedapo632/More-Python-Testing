
class TokenInfo:
    def __init__(self, typeName: str, value: str, keep = True):
        self.typeName = typeName
        self.value = value
        self.keep = keep


class Token:
    def __init__(self, tokentype: str, value: any):
        self.tokenType = tokentype
        self.value = value


    def get_type(self) -> str:
        return self.tokenType
    

    def get_value(self) -> any:
        return self.value
    

    def __str__(self) -> str:
        return f"{self.tokenType}: '{str(self.value)}'"


class Tokenizer:
    def __init__(self, types: list[TokenInfo]):
        self.types = types


    def tokenize_txt(self, text: str) -> list[Token]:
        tokens = []
        last_token = ""
        i = 0

        while i < len(text):
            stop = False

            for tokType in self.types:
                if text.startswith(tokType.value, i):
                    if last_token:
                        tokens.append(Token(self.label_token(last_token), last_token))
                        last_token = ""

                    end = self.get_end_of(text, tokType, i)
                    
                    if tokType.keep:
                        tokens.append(Token(tokType.typeName, text[i:end]))

                    i = end
                    stop = True
                    break

            if stop:
                continue

            last_token += text[i]
            i += 1

        if last_token:
            tokens.append(Token(self.label_token(last_token), last_token))

        return tokens


    def get_end_of(self, text: str, delimiter: TokenInfo, offset: int) -> int:
        return offset + len(delimiter.value)


    def label_token(self, text: str) -> str:
        return "unknown"


class ExprTokenizer(Tokenizer):
    def __init__(self):
        super().__init__([
            TokenInfo("operator", "<<"),
            TokenInfo("operator", ">>"),
            TokenInfo("operator", "+"),
            TokenInfo("operator", "-"),
            TokenInfo("operator", "*"),
            TokenInfo("operator", "/"),
            TokenInfo("operator", "%"),
            TokenInfo("operator", "&"),
            TokenInfo("operator", "^"),
            TokenInfo("operator", "|"),
            TokenInfo("open-expr", "("),
            TokenInfo("close-expr", ")"),
            TokenInfo("open-list", "["),
            TokenInfo("close-list", "]"),
            TokenInfo("open-body", "{"),
            TokenInfo("close-body", "}"),
            TokenInfo("big-string", "\""),
            TokenInfo("little-string", "'"),
            TokenInfo("operator", " ", keep = False),
            TokenInfo("operator", "\t", keep = False),
            TokenInfo("operator", "\n", keep = False)
        ])


    def get_end_of(self, text: str, delimiter: TokenInfo, offset: int) -> int:
        if delimiter.value == "\"":
            i = offset + 1

            while i < len(text):
                if text.startswith("\\\\", i) or text.startswith("\\\"", i):
                    i += 2
                    continue
                elif text[i] == "\"":
                    return i + 1
                
                i += 1
                
            raise Exception("End of big-string not found")
        elif delimiter.value == "'":
            i = offset + 1

            while i < len(text):
                if text.startswith("\\\\", i) or text.startswith("\\'", i):
                    i += 2
                    continue
                elif text[i] == "'":
                    return i + 1
                
                i += 1
                
            raise Exception("End of little-string not found")
        else:
            return super().get_end_of(text, delimiter, offset)
        

    def is_number(self, text: str) -> bool:
        if text[-1] in "fl":
            text = text[:-1]

        if text.isnumeric():
            return True
        elif "." in text:
            if text.split(".")[0].isnumeric() and text.split(".")[1].isnumeric():
                return True
            
        return False
    

    def label_token(self, text: str) -> str:
        if text[-1] == "f" and self.is_number(text):
            return "float"
        elif text[-1] == "l" and self.is_number(text):
            return "long"
        elif self.is_number(text) and not "." in text:
            return "int"
        elif self.is_number(text) and "." in text:
            return "double"
        
        return "identifier"


class ExprEvaluator:
    def __init__(self):
        pass


    def eval_token_list(self, t: list[Token]) -> Token:
        levels = [
            {
                "direction": "right",
                "operators": ["*", "/", "%"]
            },

            {
                "direction": "right",
                "operators": ["+", "-"]
            },

            {
                "direction": "right",
                "operators": ["<<", ">>"]
            },

            { "direction": "right", "operators": ["&"] },
            { "direction": "right", "operators": ["^"] },
            { "direction": "right", "operators": ["|"] }
        ]

        for level in levels:
            r = range(len(tokens)) if level["direction"] == "right" else range(len(tokens) - 1, -1, -1)

            for i in r:
                if tokens[i].get_type() == "operator":
                    if tokens[i].get_value() in level["operators"]:
                        result = self.eval_pair(tokens[i - 1], tokens[i + 1], tokens[i])

                        if level["direction"] == "right":
                            tokens[i + 1] = result
                            tokens[i] = None
                            tokens[i - 1] = None
                        else:
                            tokens[i - 1] = result
                            tokens[i] = None
                            tokens[i + 1] = None

            for i in range(len(tokens) - 1, -1, -1):
                if tokens[i] == None:
                    tokens.pop(i)

        return self.eval_token(tokens[0])


    def eval_token(self, token: Token) -> Token:
        return token


    def eval_pair(self, left: Token, right: Token, operator: Token) -> Token:
        match operator.get_value():
            case "+":
                return self.add(self.eval_token(left), self.eval_token(right))
            case "-":
                return self.sub(self.eval_token(left), self.eval_token(right))
            case "*":
                return self.mul(self.eval_token(left), self.eval_token(right))
            case "/":
                return self.div(self.eval_token(left), self.eval_token(right))
            case "<<":
                return self.lshift(self.eval_token(left), self.eval_token(right))
            case ">>":
                return self.rshift(self.eval_token(left), self.eval_token(right))
            case "%":
                return self.mod(self.eval_token(left), self.eval_token(right))
            case "&":
                return self.bwand(self.eval_token(left), self.eval_token(right))
            case "^":
                return self.bwxor(self.eval_token(left), self.eval_token(right))
            case "|":
                return self.bwor(self.eval_token(left), self.eval_token(right))
            
        return Token("none-type", "NULL")


    def validate_operators(self, left: Token, right: Token, valid_types: list[str]):
        if not left.get_type() in valid_types or not right.get_type() in valid_types:
            raise Exception(f"Unsuported operator for operands of type '{left.get_type()}' and '{right.get_type()}'")


    def higher_type_cast(self, left: Token, right: Token) -> str:
        operators = ["int", "long", "float", "double", "little-string", "big-string"]
        i1 = operators.index(left.get_type())
        i2 = operators.index(right.get_type())

        if i1 > i2:
            return left.get_type()
        
        return right.get_type()
    

    def parse_value(self, token: Token) -> any:
        match token.get_type():
            case "int":
                return int(token.value)
            case "long":
                return int(token.value.replace("l", ""))
            case "float":
                return float(token.value.replace("f", ""))
            case "double":
                return float(token.value)
            case "little-string":
                return str(token.value)[1:-1]
            case "big-string":
                return str(token.value)[1:-1]
            
        return token.value
    

    def make_value(self, token_type: str, value: any) -> str:
        match token_type:
            case "float":
                return str(value) + "f"
            case "long":
                return str(value) + "l"
            case "little-string":
                return "'" + value + "'"
            case "big-string":
                return '"' + value + '"'
            
        return str(value)


    def add(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long", "float", "double", "little-string", "big-string"])
        higher_type = self.higher_type_cast(left, right)
        return Token(higher_type, self.make_value(higher_type, self.parse_value(left) + self.parse_value(right)))


    def sub(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long", "float", "double"])
        higher_type = self.higher_type_cast(left, right)
        return Token(higher_type, self.make_value(higher_type, self.parse_value(left) - self.parse_value(right)))


    def mul(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long", "float", "double"])
        higher_type = self.higher_type_cast(left, right)
        return Token(higher_type, self.make_value(higher_type, self.parse_value(left) * self.parse_value(right)))


    def div(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long", "float", "double"])
        higher_type = self.higher_type_cast(left, right)
        return Token(higher_type, self.make_value(higher_type, self.parse_value(left) / self.parse_value(right)))


    def lshift(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long"])
        return Token("int", self.parse_value(left.value) << self.parse_value(right.value))
    
    
    def mod(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long"])
        return Token("int", self.parse_value(left.value) % self.parse_value(right.value))
    

    def bwand(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long"])
        return Token("int", self.parse_value(left.value) & self.parse_value(right.value))
    
    
    def bwxor(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long"])
        return Token("int", self.parse_value(left.value) ^ self.parse_value(right.value))
    

    def bwor(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long"])
        return Token("int", self.parse_value(left.value) | self.parse_value(right.value))


    def rshift(self, left: Token, right: Token) -> Token:
        self.validate_operators(left, right, ["int", "long"])
        return Token("int", self.parse_value(left.value) >> self.parse_value(right.value))


if __name__ == "__main__":
    tokenizer = ExprTokenizer()
    tokens = tokenizer.tokenize_txt("10 + 30.4 + 454.0f + 43.2 + 20")
    # for token in tokens: print(token)

    evaluator = ExprEvaluator()
    result = evaluator.eval_token_list(tokens)
    print(result)
    #print(30 + 500 * 10 + 20 + 30)
