from sys import argv

from Levenshtein import distance

from autosub.regressor import piecewise
from autosub.formatters import srt_parser
from autosub.formatters import srt_formatter


def score(s1, s2):
    return distance(s1[1].lower(), s2[1].lower()) / max(len(s1[1]), len(s2[1]))


def fuzzy_match(srt1, srt2):
    i = 0
    j = 0
    x = []
    y = []
    while i < len(srt1) and j < len(srt2):
        scores = [(score(srt1[i], srt2[k]), k) for k in range(max(0, j - 100), min(len(srt2), j + 100))]
        scores.sort()
        best = scores[0]
        if best[0] < 0.3:
            # print(str(best[0]) + " " + str(srt1[i].start) + " " + srt1[i].text + " | " + str(srt2[best[1]].start) + " " + srt2[best[1]].text)
            x.append(srt1[i][0][0])
            y.append(srt2[best[1]][0][0])
            j = best[1] + 1
        i = i + 1

    model = piecewise(x, y, 0.5)

    # print(model)
    # figure()
    # plot(x, y, 'ro')
    # all_x = [s.start.ordinal for s in srt1]
    # plot(all_x, model.predict(all_x))
    # show()

    return model


def convert_with_fuzzy_match(text_source, time_source):
    model = fuzzy_match(text_source, time_source)
    print(model)
    res = [((model.predict([srt[0][0]])[0], model.predict([srt[0][1]])[0]), srt[1]) for srt in text_source]
    return res


if __name__ == '__main__':
    if len(argv) < 4:
        print("Usage: fuzzy_match.py text_source time_source output")
        print("Finds the best pairing of lines from the two input files")
        print("using the Levenshtein distance and the Hungarian algorithm")

    srt1 = srt_parser(argv[1])
    srt2 = srt_parser(argv[2])
    fixed = convert_with_fuzzy_match(srt1, srt2)
    srt_fixed = srt_formatter(fixed)
    with open(argv[3], 'wb') as output_file:
        output_file.write(srt_fixed.encode("utf-8"))
