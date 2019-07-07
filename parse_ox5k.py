from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import re
import collections
import pathlib2 as pl

import PyPDF2
import requests

HEADERS = {
    'Accept'         : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    'Accept-Encoding': "gzip, deflate, br",
    'Accept-Language': "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
    'Cache-Control'  : "no-cache",
    'Connection'     : "keep-alive",
    'User-Agent'     : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36",
}

base_url = "https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/"
pdf_files = [("The%20Oxford%203000.pdf", "ox3k.pdf"), ("The%20Oxford%205000.pdf", "ox5k.pdf")]

for in_fn, out_fn in pdf_files:
    url = base_url + in_fn
    path = pl.Path(out_fn)
    if path.exists():
        continue

    print("downloading", url)
    resp = requests.get(url, headers=HEADERS)
    with path.open(mode="wb") as fobj:
        fobj.write(resp.content)


GRAMMAR_QUALIFIERS = {
    "n"         : "noun",
    "v"         : "verb",
    "noun"      : "noun",
    "adj"       : "adjective",
    "adv"       : "adverb",
    "prep"      : "preposition",
    "conj"      : "conj",
    "pron"      : "pronoun",
    "number"    : "number",
    "exclam"    : "exclamation",
    "det"       : "det",
    "modal"     : "modal-verb",
    "inffnitive": "inffnitive",
    "marker"    : "marker",
    "deffnite"  : "definite",
    "article"   : "article",
    "auxiliary" : "auxiliary",
}

LANG_LEVEL_QUALIFIERS = {"A1", "A2", "B1", "B2", "C1", "C2"}


WORD_SEP_RE = re.compile(r"([ABC][123])([A-Za-z']+[a-z]*)")


def parse_words(text):
    text = text.split("from A1 to B2 level."  , 1)[-1]
    text = text.split("which are listed here.", 1)[-1]

    text = text.replace("Oxford 3000Ž", "")
    text = text.replace("Oxford 5000Ž", "")

    text = text.replace("\n"       , "")
    text = text.replace("1 / 8˜e"  , "")
    text = text.replace("2 / 8˜e"  , "")
    text = text.replace("3 / 8˜e"  , "")
    text = text.replace("4 / 8˜e"  , "")
    text = text.replace("5 / 8˜e"  , "")
    text = text.replace("6 / 8˜e"  , "")
    text = text.replace("7 / 8˜e"  , "")
    text = text.replace("8 / 8˜e"  , "")
    text = text.replace("11 / 11˜e", "")
    text = text.replace("10 / 11˜e", "")
    text = text.replace("1 / 11˜e" , "")
    text = text.replace("2 / 11˜e" , "")
    text = text.replace("3 / 11˜e" , "")
    text = text.replace("4 / 11˜e" , "")
    text = text.replace("5 / 11˜e" , "")
    text = text.replace("6 / 11˜e" , "")
    text = text.replace("7 / 11˜e" , "")
    text = text.replace("8 / 11˜e" , "")
    text = text.replace("9 / 11˜e" , "")

    text = text.replace("© Oxford University Press", "")
    # decode ligatures (I think)
    text = text.replace("˙", "-")
    text = text.replace("™", "'")
    text = text.replace("˚", "ffi")
    text = text.replace("˝", "fl")
    text = text.replace("˛", "fi")
    text = text.replace("˜", "ff")
    text = text.replace("ˆ", "")
    text = text.replace("ˇ", "")

    text, n = WORD_SEP_RE.subn(r"\1#<>#\2", text)
    text = "#<>#" + text.strip()
    for line in text.split("#<>#"):
        if not line:
            continue
        word, qualifiers_text = line.split(" ", 1)
        if re.search(r"[^A-Z'a-z\-]+", word):
            print("unexpected chars in:", word)

        qualifiers_text = qualifiers_text.replace(",", " ")
        qualifiers_text = qualifiers_text.replace("/", " ")
        qualifiers_text = qualifiers_text.replace(".", " ")
        if ")" in qualifiers_text:
            qualifiers_text = qualifiers_text.split(")")[-1]
        qualifiers = qualifiers_text.split(" ")
        qualifiers = [q.strip() for q in qualifiers if q.strip()]

        lang_level = None
        for qualifier in reversed(qualifiers):
            if qualifier in LANG_LEVEL_QUALIFIERS:
                lang_level = qualifier
            elif qualifier in GRAMMAR_QUALIFIERS:
                assert lang_level
                yield lang_level, word, qualifier
            else:
                print("???", repr(line), repr(qualifier))


_test_text = """
bat n. B2, v. C1
besides prep., adv. B2
alert v., n., adj. C1
alien n. B2, adj. C1
"""


_expected = [
    ("C1", "bat"    , "v"),
    ("B2", "bat"    , "n"),
    ("B2", "besides", "adv"),
    ("B2", "besides", "prep"),
    ("C1", "alert"  , "adj"),
    ("C1", "alert"  , "n"),
    ("C1", "alert"  , "v"),
    ("C1", "alien"  , "adj"),
    ("B2", "alien"  , "n"),
]

_test_result = list(parse_words(_test_text))
assert _test_result == _expected

ox3k_pdf_path = pl.Path("ox3k.pdf")
ox5k_pdf_path = pl.Path("ox5k.pdf")


for pdf_path in [ox3k_pdf_path, ox5k_pdf_path]:
    tsv_name = pdf_path.name.split(".")[0] + ".tsv"
    tsv_path = pdf_path.parent / tsv_name
    if tsv_path.exists():
        continue

    words = []

    with pdf_path.open(mode="rb") as fobj:
        reader = PyPDF2.PdfFileReader(fobj)
        for pagenum in range(1, reader.numPages):
            page = reader.getPage(pagenum)
            text = page.extractText()
            for lang_level, word, word_kind in parse_words(text):
                words.append((lang_level, word, word_kind))

    words.sort()

    with tsv_path.open(mode="w", encoding="utf-8") as fobj:
        for word_item in words:
            line = "\t".join(word_item) + "\n"
            fobj.write(line)


ox3k_tsv_path = pl.Path("ox3k.tsv")
ox5k_tsv_path = pl.Path("ox5k.tsv")

word2lang = {}

for tsv_path in [ox3k_tsv_path, ox5k_tsv_path]:
    with tsv_path.open(mode="r", encoding="utf-8") as fobj:
        for line in fobj:
            lang_level, word, word_kind = line.strip().split("\t")
            if word_kind != "n":
                continue
            if word in word2lang:
                assert word2lang[word] <= lang_level
            else:
                word2lang[word] = lang_level

words_by_lang = collections.defaultdict(list)

for word, lang in word2lang.items():
    words_by_lang[lang].append(word)


for lang_level, words in words_by_lang.items():
    words.sort(key=len)
    for i, word in enumerate(words):
        print(lang_level, word.ljust(20), end="  ")
        if (i + 1) % 4 == 0:
            print()
    print()
