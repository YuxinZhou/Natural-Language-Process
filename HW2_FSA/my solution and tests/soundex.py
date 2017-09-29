from fst import FST
import string, sys
from fsmutils import composechars, trace


def letters_to_numbers():
    """
    Returns an FST that converts letters to numbers as specified by
    the soundex algorithm
    """
    # Let's define our first FST
    f1 = FST('soundex-generate')
    group0 = 'aehiouwyAEHIOUWY'
    group1 = 'bfpvBFPV'
    group2 = 'cgjkqsxzCGJKQSXZ'
    group3 = 'dtDT'
    group4 = 'lL'
    group5 = 'MNmn'
    group6 = 'rR'
    # Indicate that '1' is the initial state
    f1.add_state('start')
    for i in range(7):
        f1.add_state('s{0}'.format(i))
    f1.initial_state = 'start'

    # Set all the final states
    for i in range(7):
        f1.set_final('s{0}'.format(i))

    # Add the rest of the arcs
    for letter in string.ascii_letters:
        if letter in group0:
            f1.add_arc('start', 's0', (letter), (letter))
            for i in range(1, 7):
                f1.add_arc('s{0}'.format(i), 's0', (letter), ())
            f1.add_arc('s0', 's0', (letter), ())
        elif letter in group1:
            f1.add_arc('start', 's1', (letter), (letter))
            for i in [0, 2, 3, 4, 5, 6]:
                f1.add_arc('s{0}'.format(i), 's1', (letter), ('1'))
            f1.add_arc('s1', 's1', (letter), ())
        elif letter in group2:
            f1.add_arc('start', 's2', (letter), (letter))
            for i in [0, 1, 3, 4, 5, 6]:
                f1.add_arc('s{0}'.format(i), 's2', (letter), ('2'))
            f1.add_arc('s2', 's2', (letter), ())
        elif letter in group3:
            f1.add_arc('start', 's3', (letter), (letter))
            for i in [0, 1, 2, 4, 5, 6]:
                f1.add_arc('s{0}'.format(i), 's3', (letter), ('3'))
            f1.add_arc('s3', 's3', (letter), ())
        elif letter in group4:
            f1.add_arc('start', 's4', (letter), (letter))
            for i in [0, 1, 2, 3, 5, 6]:
                f1.add_arc('s{0}'.format(i), 's4', (letter), ('4'))
            f1.add_arc('s4', 's4', (letter), ())
        elif letter in group5:
            f1.add_arc('start', 's5', (letter), (letter))
            for i in [0, 1, 2, 3, 4, 6]:
                f1.add_arc('s{0}'.format(i), 's5', (letter), ('5'))
            f1.add_arc('s5', 's5', (letter), ())
        elif letter in group6:
            f1.add_arc('start', 's6', (letter), (letter))
            for i in [0, 1, 2, 3, 4, 5]:
                f1.add_arc('s{0}'.format(i), 's6', (letter), ('6'))
            f1.add_arc('s6', 's6', (letter), ())
    return f1

    # The stub code above converts all letters except the first into '0'.
    # How can you change it to do the right conversion?


def truncate_to_three_digits():
    """
    Create an FST that will truncate a soundex string to three digits
    """

    # Ok so now let's do the second FST, the one that will truncate
    # the number of digits to 3
    f2 = FST('soundex-truncate')

    # Indicate initial and final states
    f2.add_state('start')
    for i in range(1, 5):
        f2.add_state('s{0}'.format(i))

    f2.initial_state = 'start'
    for i in range(1, 5):
        f2.set_final('s{0}'.format(i))

    # Add the arcs
    for letter in string.letters:
        f2.add_arc('start', 's1', (letter), (letter))

    for n in range(10):
        f2.add_arc('start', 's2', (str(n)), (str(n)))
        f2.add_arc('s1', 's2', (str(n)), (str(n)))
        f2.add_arc('s2', 's3', (str(n)), (str(n)))
        f2.add_arc('s3', 's4', (str(n)), (str(n)))
        f2.add_arc('s4', 's4', (str(n)), ())

    return f2

    # The above stub code doesn't do any truncating at all -- it passes letter and number input through
    # what changes would make it truncate digits to 3?


def add_zero_padding():
    # Now, the third fst - the zero-padding fst
    f3 = FST('soundex-padzero')

    f3.add_state('start')
    f3.add_state('1')
    f3.add_state('1a')
    f3.add_state('1b')
    f3.add_state('2')

    f3.initial_state = 'start'
    f3.set_final('2')

    f3.add_arc('1', '1a', (), ('0'))
    f3.add_arc('1a', '1b', (), ('0'))
    f3.add_arc('1b', '2', (), ('0'))

    for letter in string.letters:
        f3.add_arc('start', '1', (letter), (letter))
    for number in xrange(10):
        f3.add_arc('start', '1a', (str(number)), (str(number)))
        f3.add_arc('1', '1a', (str(number)), (str(number)))
        f3.add_arc('1a', '1b', (str(number)), (str(number)))
        f3.add_arc('1b', '2', (str(number)), (str(number)))
    return f3

    # The above code adds zeroes but doesn't have any padding logic. Add some!


if __name__ == '__main__':
    user_input = raw_input().strip()
    f1 = letters_to_numbers()
    f2 = truncate_to_three_digits()
    f3 = add_zero_padding()

    if user_input:
        print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))
        user_input = raw_input().strip()

    # while user_input:
    #     print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))
    #     user_input = raw_input().strip()