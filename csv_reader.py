#!/usr/bin/env python3

import csv
from pprint import pprint


def main():
    with open('firms.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect='unix', delimiter=';')
        i = 0
        uniq_phones = []
        for row in reader:
            if row['phone'] and row['phone'] not in uniq_phones:
                uniq_phones.append(row['phone'])
                pprint(dict(row))
                i += 1
                print(i)


if __name__ == '__main__':
    main()
