"""
Module creates individual ortho-profiles for a set of languages.
"""

from collections import defaultdict
from unicodedata import normalize
from csvw.dsv import UnicodeDictReader


with UnicodeDictReader('cldf/forms.csv') as reader:
    data = [row for row in reader]

with UnicodeDictReader('etc/archive/orthography.tsv', delimiter="\t") as ortho:
    profile = {}
    for row in ortho:
        profile[normalize('NFC', row['Grapheme'])] = row['IPA']

languages = set([row['Language_ID'] for row in data])

profiles = {language: defaultdict(int) for language in languages}

errors = {}


lexemes = {}
for row in data:
    entry = list(row["Value"])
    for char in entry:
        # print(char)
        char = normalize('NFC', char)
        profiles[row['Language_ID']][char, profile.get(char, '?'+char)] += 1

for language in languages:
    with open('etc/orthography/'+language+'.tsv', 'w', encoding="utf8") as f:
        f.write('Grapheme\tIPA\tFrequency\n')
        for (char, ipa), freq in profiles[language].items():
            f.write(f'{char}\t{ipa}\t{freq}\n')
            if ipa.startswith('?'):
                errors[char] = ipa[1:]

if len(errors) > 1:
    with open('etc/addons.tsv', 'w', encoding="utf8") as f:
        for a, b in errors.items():
            f.write(a+'\t'+b+'\n')
