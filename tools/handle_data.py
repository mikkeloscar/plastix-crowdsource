#!/usr/bin/python

import csv
import sys

def parse_datafile(path):
    rows = []
    with open(path, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\"',
                escapechar='\\')
        for i, row in enumerate(reader):
            r = {
                    "survey_id": row[0],
                    "ex_type": row[1],
                    "ex_id": row[2],
                    "choice": row[3],
                    "answer": row[4],
                    "more": row[5],
                    "easy": row[6],
                    "date": row[7]
                }
            rows.append(r)
    return rows

def print_data(data):
    for row in data:
        print(parse_row(row))


def parse_row(row):
    return ','.join([
        row["survey_id"],
        row["ex_type"],
        row["ex_id"],
        row["choice"],
        wrap(row["answer"]),
        wrap(row["more"]),
        wrap(row["easy"]),
        row["date"]
        ])

def wrap(field):
    return '"%s"' % str(field).replace("\"", "\\\"")


def remove_id(survey_id, data):
    new_data = []
    for d in data:
        if d["survey_id"] != survey_id:
            new_data.append(d)
    return new_data


def remove_invalid_answers(data):
    new_data = []
    for d in data:
        # edit this to remove what is needed
        if d["id"]:
            pass


def main():
    data = parse_datafile(sys.argv[1])

    if len(sys.argv) > 3 and sys.argv[2] == "id":
        data = remove_id(sys.argv[3], data)
    print_data(data)

if __name__ == "__main__":
    main()
