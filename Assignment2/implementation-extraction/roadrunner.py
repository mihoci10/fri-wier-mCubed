from html.parser import HTMLParser

class CustomParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tokens = []

    def handle_data(self, data):
        data = data.strip().lower()
        if data:
            self.tokens.append(("data", data))

    def handle_starttag(self, tag, _):
        self.tokens.append(("start", tag))

    def handle_endtag(self, tag):
        self.tokens.append(("end", tag))

def _are_tokens_matching(t1, t2, matchData):
    if matchData:
        return t1[0] == t2[0] and  t1[1] == t2[1]
    else:
        return (t1[0] == 'data') and (t2[0] == 'data')
    
def _get_iter_end(tokens: list[tuple[str, str]], i):
    start = i
    while i < len(tokens):
        if tokens[i][0] == 'end' and tokens[i][1] == tokens[start][1]:
            return i
        i+=1
    return None
    
def _get_iter_start(tokens: list[tuple[str, str]], i):
    end = i
    while i >= 0:
        if tokens[i][0] == 'start' and tokens[i][1] == tokens[end][1]:
            return i
        i-=1
        
    return None

def _join_wrappers(wrapper: list[tuple[str, str]], iter_wrapper: list[tuple[str, str]], iter_tag: str):

    i = len(wrapper) - 1
    startI = None

    while i > 0:
        if wrapper[i][0] == 'option':
            i-=1
            continue

        if wrapper[i][0] == 'end' and wrapper[i][1] == iter_tag:
            endI = i

            while i > 0:
                if wrapper[i][0] == 'start' and wrapper[i][1] == iter_tag:
                    startI = i
                    break
                i-=1
        else:
            break
        i-=1

    if startI == None or endI == None:
        return None
    
    iter_token = ('iter', iter_wrapper)
    return wrapper[:startI] + [iter_token]
    
def _get_tokens_iterative(tokens: list[tuple[str, str]], i, wrapper: list[tuple[str, str]]):
        t = tokens[i]
        tprev = tokens[i - 1]
        
        if tprev[0] == 'end' and t[0] == 'start' and  tprev[1] == t[1]:

            endI = _get_iter_end(tokens, i)
            if endI == None:
                return None
            
            startI = _get_iter_start(tokens, i - 1)
            if startI == None:
                return None
            
            last_iter = tokens[startI: i]
            cur_iter = tokens[i: endI + 1]

            iter_wrapper = _execute(last_iter, cur_iter, 0, 0, [])
            if iter_wrapper == None:
                return None
            
            return _join_wrappers(wrapper, iter_wrapper, t[1])
        
def _get_next_token(tokens: list[tuple[str, str]], i):
    if tokens[i][0] == 'start':
        return _get_iter_end(tokens, i) + 1
    else:
        return i + 1
        
def _get_tokens_optional(tokens1: list[tuple[str, str]], tokens2: list[tuple[str, str]], i1, i2):
        t1 = tokens1[i1]
        t2 = tokens2[i2]

        t1next = None
        if i1 < len(tokens1) - 1:
            t1next = tokens1[i1 + 1]
        t2next = None
        if i2 < len(tokens2) - 1:
            t2next = tokens2[i2 + 1]

        if t2next != None and _are_tokens_matching(t1, t2next, True):
            return (('option', t2[1]), None)
        elif t1next != None and _are_tokens_matching(t2, t1next, True):
            return (None, ('option', t1[1]))

        return (None, None)

def _execute(tokens1: list[tuple[str, str]], tokens2: list[tuple[str, str]], i1: int, i2: int, result: list[tuple[str, str]]):
    
    if (i1 == len(tokens1) and i2 == len(tokens2)):
        return result
    elif (i1 == len(tokens1) or i2 == len(tokens2)):
        return None
    
    t1 = tokens1[i1]
    t2 = tokens2[i2]

    if _are_tokens_matching(t1, t2, True):
        result.append((t1[0], t1[1]))
        return _execute(tokens1, tokens2, i1 + 1, i2 + 1, result)
    elif _are_tokens_matching(t1, t2, False):
        result.append(('data', '#PCDATA'))
        return _execute(tokens1, tokens2, i1 + 1, i2 + 1, result)
    else:
        iter_wrapper1 = _get_tokens_iterative(tokens1, i1, result)
        if iter_wrapper1 != None:
            endI = _get_iter_end(tokens1, i1)
            return _execute(tokens1, tokens2, endI + 1, i2, iter_wrapper1)
        
        iter_wrapper2 = _get_tokens_iterative(tokens2, i2, result)
        if iter_wrapper2 != None:
            endI = _get_iter_end(tokens2, i2)
            return _execute(tokens1, tokens2, i1, endI + 1, iter_wrapper2)
        
        (o1, o2) = _get_tokens_optional(tokens1, tokens2, i1, i2)

        if o1 != None:
            result.append(o1)
            return _execute(tokens1, tokens2, i1, i2 + 1, result)
        if o2 != None:
            result.append(o2)
            return _execute(tokens1, tokens2, i1 + 1, i2, result)
        
        if a > 0 or b > 0:
            return _execute(tokens1, tokens2, i1 + b, i2 + a, result)
        
def _parse_results(results, inset=0):
    result = ''
    for token in results:
        if token[0] == 'start':
            result += f'{'\t'*inset}<{token[1]}>'
            inset += 1
        elif token[0] == 'end':
            inset -= 1
            result += f'{'\t'*inset}</{token[1]}>'
        elif token[0] == 'data':
            result += f'{'\t'*inset}#data'
        elif token[0] == 'option':
            result += f'{'\t'*inset}( {token[1]} )?'
        elif token[0] == 'iter':
            result += f'{'\t'*inset}(\n {_parse_results(token[1], inset+1)} \n{'\t'*inset})+'

        result += '\n'

    return result


def run(page1, page2):

    parser1 = CustomParser()
    parser1.feed(page1)
    tokens1 = parser1.tokens

    parser2 = CustomParser()
    parser2.feed(page2)
    tokens2 = parser2.tokens

    result = _execute(tokens1, tokens2, 0, 0, [])

    return(_parse_results(result))

f1 = open('Assignment2/input-extraction/overstock.com/jewelry01.html')
f2 = open('Assignment2/input-extraction/overstock.com/jewelry02.html')

s1 = '\n'.join(f1.readlines())
s2 = '\n'.join(f2.readlines())

run(s1, s2)