import re
# import lxml
import json
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
# from lxml import etree


def parse(file):
    data_m = []
    data_l = []
    sents = file.split('<sentence')[1:]
    for s in sents:
        s_new = s.split('</sentence>')[0]
        s_new = '<sentence' + s_new + '</sentence>'
        f = open('sent_temp.xml', 'w', encoding='utf-8')
        f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?><annotation version="0.12" revision="4372100">'+s_new+'</annotation>')
        f.close()
        tree = etree.parse('sent_temp.xml')
        data = parse_sent(tree)
        data_sent_m = data[0]
        data_sent_l = data[1]
        if len(data_sent_m) != 0:
            for word in data_sent_m:
                data_m.append(word)
        if len(data_sent_l) != 0:
            for word in data_sent_l:
                data_l.append(word)
    return data_m, data_l


def parse_sent(tree):
    lists = tree.xpath('//l')
    words = []
    ambig = []
    poses = []
    true_poses = []
    i = 0
    for token in lists:
        i +=1
        if (token[0].values()[0] != 'Erro') & (token[0].values()[0] != 'UNKN'):
            word = token.get('t')
            if (is_word(word) == False) & (i != len(lists)-1):
                continue
            if is_num(word):
                word = '_NUM_'
            words.append(word)
            true_poses.append(token[0].values()[0])
            tags = morph.parse(word)[:3]
            pos = []
            for t in tags:
                if t.tag.POS not in pos:
                    if t.tag.POS == None:
                        pos.append('UNKN')
                    else:
                        pos.append(t.tag.POS)
            if len(pos) > 1:
                ambig.append([True, morph.parse(word)[0].tag.POS, morph.parse(word)[0].score])
                poses.append('/'.join(pos))
            else:
                poses.append(token[0].values()[0])
                ambig.append([False])
    result_morph = ambig_morphsearch(ambig, poses, true_poses)
    result_lex = ambig_lexsearch(ambig, words, true_poses)
    return result_morph, result_lex

def is_word(word):
    if re.match(r'[а-я]+', word.lower()):
        return True
    if is_num(word):
        return True
    return False

def is_num(word):
    if re.match(r'[0-9]',word):
        return True
    return False

def ambig_morphsearch(ambig, poses, true_poses):
    data = []
    for i in range(len(true_poses)):
        if ambig[i][0] == True:
            dic = {}
            dic_context = {}
            dic_context['tag'] = true_poses[i]
            dic_context['context'] = make_context(poses, i)
            dic_context['pymorphy'] = ambig[i][1:]
            dic[poses[i]] = dic_context
            data.append(dic)
    return data

def ambig_lexsearch(ambig, words, true_poses):
    data = []
    for i in range(len(ambig)):
        if ambig[i][0] == True:
            dic = {}
            dic_context = {}
            dic_context['tag'] = true_poses[i]
            dic_context['context'] = make_context(words, i)
            dic_context['pymorphy'] = ambig[i][1:]
            dic[words[i]] = dic_context
            data.append(dic)
    return data

def make_context(words, i):
    context = ''
    if i == 1:
        context += '_0_ %s _WORD_ ' % words[i-1]
    if i == 0:
        context += '_0_ _0_ _WORD_ '
    if i > 1:
        context += '%s %s _WORD_ ' % (words[i-2], words[i-1])
    if len(words) - i == 2:
        context += '%s _0_' % words[i+1]
    if len(words) - i == 1:
        context += '_0_ _0_'
    if len(words) - i > 2:
        context += '%s %s' % (words[i+1], words[i+2])
    return context

def writeInJson(t, name):
    f = open(name+'.json', 'w', encoding = 'utf-8')
    json.dump(t, f, indent = 2, ensure_ascii = False)
    f.close()


if __name__ == '__main__':
    f1 = open('annot.opcorpora.no_ambig.xml', 'r', encoding = 'utf-8')
    file = f1.read()
    f1.close()
    data_morph = parse(file)[0]
    data_lex = parse(file)[1]
    writeInJson(data_morph, 'data_morph')
    writeInJson(data_lex, 'data_lex')
