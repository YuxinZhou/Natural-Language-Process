import sys
from fst import FST
from fsmutils import trace
from fsmutils import composewords

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
    "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                     "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                     "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'


def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
        "Integer out of bounds"
    return list("%03i" % integer)


def french_count():
    f = FST('french')

    f.add_state('start')
    f.add_state('a0')
    f.add_state('a1')
    # state b0 - state b6
    for i in range(7):
        f.add_state('b{0}'.format(i))
    f.add_state('end')

    f.initial_state = 'start'
    f.set_final('end')

    # hundreds
    # a different state for hundred digit = 1
    f.add_arc('start', 'a1', ['0'], [])
    f.add_arc('start', 'a0', ['1'], [kFRENCH_TRANS[100]])
    for ii in range(2, 10):
        f.add_arc('start', 'a0', [str(ii)], [kFRENCH_TRANS[ii] + ' ' + kFRENCH_TRANS[100]])

    # tens
    f.add_arc('a0', 'b0', ['0'], [])
    f.add_arc('a0', 'b1', ['1'], [])
    for ii in range(2, 7):
        f.add_arc('a0', 'b2', [str(ii)], [kFRENCH_TRANS[ii * 10]])
    f.add_arc('a0', 'b3', ['7'], [kFRENCH_TRANS[60]])
    f.add_arc('a0', 'b4', ['8'], [kFRENCH_TRANS[4] + ' ' + kFRENCH_TRANS[20]])
    f.add_arc('a0', 'b5', ['9'], [kFRENCH_TRANS[4] + ' ' + kFRENCH_TRANS[20]])

    f.add_arc('a1', 'b6', ['0'], [])
    f.add_arc('a1', 'b1', ['1'], [])
    for ii in range(2, 7):
        f.add_arc('a1', 'b2', [str(ii)], [kFRENCH_TRANS[ii * 10]])
    f.add_arc('a1', 'b3', ['7'], [kFRENCH_TRANS[60]])
    f.add_arc('a1', 'b4', ['8'], [kFRENCH_TRANS[4] + ' ' + kFRENCH_TRANS[20]])
    f.add_arc('a1', 'b5', ['9'], [kFRENCH_TRANS[4] + ' ' + kFRENCH_TRANS[20]])

    for ii in xrange(10):
        # 0~9
        if ii == 0:
            f.add_arc('b0', 'end', [str(ii)], [])
        else:
            f.add_arc('b0', 'end', [str(ii)], [kFRENCH_TRANS[ii]])
        # 10~19
        if ii <= 6:
            f.add_arc('b1', 'end', [str(ii)], [kFRENCH_TRANS[ii + 10]])
        else:
            f.add_arc('b1', 'end', [str(ii)], [kFRENCH_TRANS[10] + ' ' + kFRENCH_TRANS[ii]])
        # 20~69
        if ii == 0:
            f.add_arc('b2', 'end', [str(ii)], [])
        elif ii == 1:
            f.add_arc('b2', 'end', [str(ii)], [kFRENCH_AND + ' ' + kFRENCH_TRANS[ii]])
        else:
            f.add_arc('b2', 'end', [str(ii)], [kFRENCH_TRANS[ii]])
        # 70~79
        if ii == 1:
            f.add_arc('b3', 'end', [str(ii)], [kFRENCH_AND + ' ' + kFRENCH_TRANS[ii + 10]])
        elif ii <= 6:
            f.add_arc('b3', 'end', [str(ii)], [kFRENCH_TRANS[ii + 10]])
        else:
            f.add_arc('b3', 'end', [str(ii)], [kFRENCH_TRANS[10] + ' ' + kFRENCH_TRANS[ii]])
        # 80~89
        if ii == 0:
            f.add_arc('b4', 'end', [str(ii)], [])
        else:
            f.add_arc('b4', 'end', [str(ii)], [kFRENCH_TRANS[ii]])
        # 90~99
        if ii <= 6:
            f.add_arc('b5', 'end', [str(ii)], [kFRENCH_TRANS[ii + 10]])
        else:
            f.add_arc('b5', 'end', [str(ii)], [kFRENCH_TRANS[10] + ' ' + kFRENCH_TRANS[ii]])
        # 0~9
        f.add_arc('b6', 'end', [str(ii)], [kFRENCH_TRANS[ii]])
    return f


if __name__ == '__main__':
    f = french_count()
    string_input = raw_input()
    user_input = int(string_input)
    # if string_input:
    #     print user_input, '-->',
    #     print " ".join(f.transduce(prepare_input(user_input)))

    while string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))
        string_input = raw_input()
        user_input = int(string_input)


