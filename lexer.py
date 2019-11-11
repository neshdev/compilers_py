import re
import collections


def get_contents(file_name):
    with open(file_name) as f:
        contents = f.read()
        return contents


def strip_string(contents):
    return contents


def lexer(statements):
    token_specifications = [
        ('INT', r'\d+'),
        ('STRING', r'"[\s\S]*"'),

        ('TYPE_ID', r'[A-Z][A-Za-z0-9_]*|SELF_TYPE|self'),
        ('OBJECT_ID', r'[a-z][A-Za-z0-9_]*'),

        # keywords
        ('KEYWORD_CLASS', r'[cC][lL][aA][sS]'),
        ('KEYWORD_ELSE', r'[eE][lL][sS][eE]'),
        ('KEYWORD_fi', r'[fF][iI]'),
        ('KEYWORD_in', r'[iI][nN]'),
        ('KEYWORD_inherits', r'[iI][nN][hH][eE][rR][iI][tT][sS]'),
        ('KEYWORD_isvoid', r'isvoid'),
        ('KEYWORD_let', r'[lL][eE][tT]'),
        ('KEYWORD_loop', r'[lL][oO][oO][pP]'),
        ('KEYWORD_pool', r'[pP][oO][lL][lL]'),
        ('KEYWORD_then', r'[tT][hH][eE][nN]'),
        ('KEYWORD_while', r'[wH][hH][iI][lL][eE]'),
        ('KEYWORD_case', r'[cC][aA][sS][eE]'),
        ('KEYWORD_esac', r'[eE][sS][aA][cC]'),
        ('KEYWORD_new', r'[nN][eE][wW]'),
        ('KEYWORD_of', r'[oO][fF]'),
        ('KEYWORD_not', r'[nN][oO][tT]'),
        ('FALSE', r'[fF][aA][lL][sS][eE]'),
        ('TRUE', r'[tT][rR][uU][eE]'),

        ('VALID_COMPARISON_EQ_OP', r'='),
        ('VALID_COMPARISON_LTEQ_OP', r'<='),
        ('VALID_COMPARISON_LT_OP', r'<'),

        ('INVALID_COMPARISON_EQ_OP', r'=='),
        ('INVALID_COMPARISON_GTEQ_OP', r'>='),
        ('INVALID_COMPARISON_GT_OP', r'>'),



        ('ARROW_OP', r'=>'),
        ('ASSIGN_OP', r'<-'),

        ('LEFT_BRACE', r'{'),
        ('RIGHT_BRACE', r'}'),

        ("BEGIN_MULTILINE_COMMENT", r'\([*]'),
        ("END_MULTILINE_COMMENT", r'\*\)'),

        ('LEFT_PAREN', r'\('),
        ('RIGHT_PAREN', r'\)'),

        ('SEMI', r';'),
        ('COLON', r':'),

        ('INLINE_COMMENT', r'\-\-.*'),
        ('WHITESPACE', r'[ \n\f\r\t]*'),

        ('PLUS_OP', r'\+'),
        ('MINUS_OP', r'-'),
        ('DIVIDE_OP', r'/'),
        ('MULT_OP', r'\*'),
        ('NEG_OP', r'~'),

        ('ERROR', r'.')

    ]

    all_patterns = [f"(?P<{t}>{r})" for (t, r) in token_specifications]
    master = "|".join(all_patterns)
    print(master)
    start = 0
    end = len(statements)
    pattern = re.compile(master)
    line_number = 1
    while(end > start):
        matched = pattern.match(statements, start)
        if matched:
            token_type = matched.lastgroup
            token_value = matched.group(0)
            col_start, col_end = matched.regs[0]
            line_number = line_number + token_value.count('\n')

            if token_type == "STRING":
                """
                Error check for string here!
                """
                valid = True
                if '\x00' in token_value:
                    valid = False
                    yield Token("ERROR", token_value, line_number, col_start, msg="Contains null character")
                if len(token_value) > 1025:
                    valid = False
                    yield Token("ERROR", token_value, line_number, col_start, msg="String longer than 1025 characers")
                if valid:
                    token_value = strip_string(token_value)
                    yield Token(token_type, token_value, line_number, col_start, "")
            elif token_type == "BEGIN_MULTILINE_COMMENT":
                idx = statements[start:].find("*)")
                line_number = line_number + statements[start:idx].count('\n')
                start = start + idx
                continue
            elif token_type not in ["WHITESPACE", "INLINE_COMMENT", "BEGIN_MULTILINE_COMMENT", "END_MULTILINE_COMMENT"]:
                yield Token(token_type, token_value, line_number, col_start, "")

            # Sometimes regex doesn't advance
            if (start == col_end):
                start = col_end+1
            else:
                start = col_end


Token = collections.namedtuple(
    'Token', ['type', 'value', 'line', 'column', 'msg'])

SMALL_COOL = "small_cool.cl"


def run():
    statement = get_contents(SMALL_COOL)
    tokens = lexer(statement)
    for x in tokens:
        print(x)


if __name__ == "__main__":
    run()
