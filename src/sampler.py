from collections import namedtuple
import itertools
import json
import random

SAMPLE_SIZES = [12, 18]
DELTA_LEVELS = [1, 2, 4]
INTERVALS = {
    "A": [1, 5],
    "B": [3, 7],
    "C": [5, 9]
}

def _generate_all_possible_sub_ranges():
    """ Generates all subranges within a certain range in a certain delta.
        Returns a tuple containing:

        lower bound (p1),
        upper bound (p2),
        key of original subrange (A, B, C)
        delta
    """
    return [
        [
            (p1, (p1 + delta), range_key, delta)
            for p1 in range(lower_bound, upper_bound - delta + 1)
        ]
        for range_key, (lower_bound, upper_bound) in INTERVALS.items()
        for delta in DELTA_LEVELS
    ]

def _choose_random_delta_range(subranges):
    return map(random.choice, subranges)

def _randomize_advantage(ranges):
    """Swaps the bounds of the range from left to right randomly.
    Like this, sometimes the left stock is better, sometimes the right.
    """
    def _swap_or_keep(p1, p2, key, delta):
        return random.choice(
            [lambda a,b,k,d: (b,a,k,d),
             lambda a,b,k,d: (a,b,k,d)]
        )(p1, p2, key, delta)
    return itertools.starmap(_swap_or_keep, ranges)


def _generate_ranges():
    # Generate all delta subranges_generate_ranges
    result = _generate_all_possible_sub_ranges()

    # Choose a random subrange for sampling
    result = _choose_random_delta_range(result)

    # Randomize which stock is the better one
    return _randomize_advantage(result)


def _permute_experimental_factors():
    """Returns a set of all experimental factors.
        Each "Block" contains:

        p1, p2, subrange key, delta, n
    """
    return itertools.chain(
        [
            (p1, p2, key, delta, n)
            for n in SAMPLE_SIZES
            for p1, p2, key, delta in _generate_ranges()
        ]
    )


def _sample_stock(percent, n):
    '''
        The Percent value comes in as an integer
        indicating 10 percent, so
        2 means .20, which is 20 Percent.
        I chose integers because they prevented
        rounding errors due to floating point arithmetics
    '''
    positive = round(n * (percent / 10))
    negative = n - positive

    positives = [1] * positive
    negatives = [0] * negative

    stock = positives + negatives
    assert len(stock) == n
    random.shuffle(stock)
    return stock


def _empirical_p_value(values):
    positive = sum(1 for v in values if v == 1)
    negative = sum(1 for v in values if v == 0)
    assert positive + negative == len(values)
    return round(positive / len(values), 2)


header = ['delta', 'p1', 'p2', 'subrange_key',
    'empirical_delta', 'empirical_p1', 'empirical_p2',
    'sample_size', 'start_with',
    'left', 'right']


Trial = namedtuple('Trial', header)


def _sample_stock_valuations(block):
    for p1, p2, subrange_key, delta, n in block:

        left  = _sample_stock(p1, n)
        right = _sample_stock(p2, n)

        empirical_p1 = _empirical_p_value(left)
        empirical_p2 = _empirical_p_value(right)
        empirical_delta = round(abs(empirical_p1 - empirical_p2), 2)

        # This randomizes whether the left or right stock
        # should start being displayed first.
        start_with = random.getrandbits(1)

        yield Trial(
            delta / 10,
            p1 / 10,
            p2 / 10,
            subrange_key,
            empirical_delta, empirical_p1, empirical_p2,
            n,
            start_with,
            left,
            right
        )


def _generate_randomized_block():
    design = _permute_experimental_factors()
    sampled_block = _sample_stock_valuations(design)
    block = list(sampled_block)
    random.shuffle(block)
    return block


class Block(object):
    def __init__(self):
        block = _generate_randomized_block()
        self.block = dict(trials=[trial._asdict() for trial in block])

    def __str__(self):
        return json.dumps(self.block)

    def __repr__(self):
        return '<Block (%s)>' % len(self.block)
