#!/usr/bin/env python

from __future__ import print_function

import nltk
from nltk.corpus import stopwords
import re
import string


stop_words = stopwords.words('english')


def is_unimportant(word):
    """Decides if a word is ok to toss out for the sentence comparisons"""
    return word in [
        '.', '!', ',', 'Page', '(', ')'] or '\'' in word or word in stop_words


def only_important(sent):
    """Just a little wrapper to filter on is_unimportant"""
    return filter(lambda w: not is_unimportant(w), sent)


def compare_sents(sent1, sent2):
    """Compare two word-tokenized sentences for shared words"""
    if not len(sent1) or not len(sent2):
        return 0
    return len(set(only_important(sent1)) & set(only_important(sent2))) / (
        (len(sent1) + len(sent2)) / 2.0)


def compare_sentences_bounded(sent1, sent2):
    # The low end of shared words to consider
    lower_bound = .15

    # The high end, since anything above this is probably SEO garbage or a
    # duplicate sentence
    upper_bound = .90

    """If the result of compare_sents is not between LOWER_BOUND and
    UPPER_BOUND, it returns 0 instead, so outliers don't mess with the sum"""
    cmpd = compare_sents(sent1, sent2)
    if lower_bound < cmpd < upper_bound:
        return cmpd
    else:
        return 0


def compute_score(sent, sents):
    """Computes the average score of sent vs the other sentences (the result of
    sent vs itself isn't counted because it's 1, and that's above
    UPPER_BOUND)"""
    if not len(sent):
        return 0
    return sum(compare_sentences_bounded(sent, sent1)
               for sent1 in sents) / float(len(sents))


def summarize_block(block):
    """Return the sentence that best summarizes block"""
    if not block:
        return None
    sents = nltk.sent_tokenize(block)
    word_sents = list(map(nltk.word_tokenize, sents))
    d = dict((compute_score(word_sent, word_sents), sent)
             for sent, word_sent in zip(sents, word_sents))
    return d[max(d.keys())]


def find_likely_body(b):
    """Find the tag with the most directly-descended <p> tags"""
    return max(b.find_all(),
               key=lambda t: len(t.find_all('p', recursive=False)))


def summarize_blocks(blocks):
    summaries = [re.sub('\s+', ' ', summarize_block(block) or '').strip()
                 for block in blocks]
    # deduplicate and preserve order
    summaries = sorted(set(summaries), key=summaries.index)
    return [re.sub('\s+', ' ', summary.strip()) for summary in summaries if
            any(c.lower() in string.ascii_lowercase for c in summary)]


def summarize_text(text, block_sep='\n\n'):
    return '\n'.join(summarize_blocks(text.split(block_sep)))
