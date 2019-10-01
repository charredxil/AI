def analyze1(text):
    num_words = len(text)
    uniq_words = set(text)
    num_uniq_words = len(uniq_words)
    avglen_uniq_words = sum(map(lambda w: len(w), uniq_words))/num_uniq_words
    avgvow_uniq_words = sum(map(lambda w: sum(map(w.lower().count, 'aeiou')), uniq_words))/num_uniq_words
    return(num_words, num_uniq_words, avglen_uniq_words, avgvow_uniq_words)

def letter_freq(text):
    count = {}
    tot = 0
    for w in text:
        wl = w.lower()
        for c in w:
            if c.isalpha():
                if c not in count: count[c] = 0
                count[c] += 1
                tot += 1
    return {l : cnt/tot for l, cnt in count.items()}
