from datetime import datetime
from pytz import UTC

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from django.conf import settings

from capitolzen.meta.states import AVAILABLE_STATES


def iterate_states(manager, manager_task):
    for state in AVAILABLE_STATES:
        if not manager(state.name).is_updating():
            manager_task.delay(state.name)
    return True


def time_convert(time):
    if isinstance(time, str):
        return UTC.localize(datetime.strptime(time, '%Y-%m-%d %I:%M:%S'))
    try:
        return UTC.localize(time)
    except ValueError:
        # Already a non-naive datetime
        return time


def summarize(content):
    if content is None:
        return ""
    language = "english"
    stemmer = Stemmer(language)
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)
    summary = ""
    # encoding and decoding clears up some issues with ascii
    # codec parsing.
    sentence_list = [
        str(sentence) for sentence in summarizer(
            PlaintextParser.from_string(
                content.encode('utf-8').strip().decode('utf-8'),
                Tokenizer(language)).document,
            settings.DEFAULT_SENTENCE_COUNT)]
    for sentence in sentence_list:
        excluded = [exclude
                    for exclude in settings.DEFAULT_EXCLUDE_SENTENCES
                    if exclude.lower() in sentence.lower()]
        word_list = sentence.split(' ')
        if settings.TIME_EXCLUSION_REGEX.search(sentence) is None \
                and len(summary) < settings.DEFAULT_SUMMARY_LENGTH \
                and len(excluded) == 0 \
                and len(word_list) > 1:
            summary += " " + sentence
    return summary.replace('&gt;', '').strip()
