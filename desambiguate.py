import pymorphy2

import re
from data import *

morph = pymorphy2.MorphAnalyzer()


def tokenize(text):
    return [word.lower() for word in re.split(r'(?!\b-\b)\W', text) if word]


def desambiguate_sent(sent):
    words = tokenize(sent)
    ambig = []
    poses = []
    result = []
    for word in words:
        tags = morph.parse(word)[:3]
        pos = []
        for t in tags:
            if t.tag.POS not in pos:
                if t.tag.POS is None:
                    pos.append('UNKN')
                else:
                    pos.append(t.tag.POS)
        if len(pos) > 1:
            ambig.append(True)
            poses.append('/'.join(pos))
        else:
            poses.append(pos[0])
            ambig.append(False)
    for i in range(len(ambig)):
        if ambig[i] is True:
            context_lex = make_context(words, i)
            context_morph = make_context(poses, i)
            result.append([words[i], context_lex, poses[i], context_morph])
    return result

if __name__ == '__main__':
    sent = input('print a sentence:\n')
    res = desambiguate_sent(sent)
    print(res)
