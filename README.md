# Scraper for PDF files from

This is a quick scraper I wrote to parse some PDF files an generate wordlists.

Usage:

```shell
git clone https://github.com/mbarkhau/oxford5k-data.git
cd oxford5k-data.git
python -m pip install -r requirements.txt
python parse_ox5k.py
downloading https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The%20Oxford%203000.pdf"
downloading https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The%20Oxford%205000.pdf"
A1 CD                    A1 TV                    A1 DVD                   A1 May
A1 box                   A1 boy                   A1 bus                   A1 car
A1 cat                   A1 cow                   A1 cup                   A1 dad
A1 day                   A1 dog                   A1 ear                   A1 egg
A1 end                   A1 eye                   A1 fun                   A1 gym
```

The parsed tsv files (as of July 2019) are included in the repo for convenience.

```shell
head ox3k.tsv
A1      CD      n
A1      DVD     n
A1      December        n
A1      February        n
A1      Friday  n
A1      I       pron
A1      January n
A1      July    n
```

The MIT License applies to the `parse_ox5k.py`. IANAL but I assume the data files `ox3k.tsv` and `ox5k.tsv` have the same copyright as the original PDF files: © Oxford University Press.

