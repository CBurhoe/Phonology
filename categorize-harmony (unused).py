import pandas as pd
from scipy.stats import chi2_contingency

# define front, mid, and back vowels
front_vowels = ['ö', 'ä', 'y']
mid_vowels = ['e', 'i']
back_vowels = ['a', 'o', 'u']

# read in the word list
with open('preprocessed-index.txt', 'r', encoding='utf-8') as f:
    words = [word.strip() for word in f.readlines()]

# categorize each word based on vowel harmony
u = open('unknown-words.txt', 'w', encoding='utf-8')
categories = []
for word in words:
    front = False
    back = False
    neutral = False
    for letter in word:
        if letter in front_vowels:
            front = True
            back = False
        elif letter in mid_vowels:
            neutral = True
        elif letter in back_vowels:
            back = True
            front = False
    if front:
        category = 'Front'
    elif back:
        category = 'Back'
    elif neutral:
        category = 'Front'
    else:
        category = 'Unknown'
        u.write(word + '\n')
    categories.append(category)
u.close()
# create a DataFrame to hold the word list and categories
df = pd.DataFrame({'Word': words, 'Vowel Harmony': categories})

front_harmony_words = df[df['Vowel Harmony'] == 'Front']['Word'].tolist()
back_harmony_words = df[df['Vowel Harmony'] == 'Back']['Word'].tolist()

# print out summary statistics
print('Number of words:', len(front_harmony_words) + len(back_harmony_words))
print('Number of front-harmony words:', len(df[df['Vowel Harmony'] == 'Front']))
print('Number of back-harmony words:', len(df[df['Vowel Harmony'] == 'Back']))
print('Number of discarded words:', len(df[df['Vowel Harmony'] == 'Unknown']))

#
#
# # define front and back harmony lists
# with open('preprocessed-index.txt', 'r', encoding='utf-8') as f:
#     words = [word.strip() for word in f.readlines()]
#
# front_harmony_words = [word for word in words if all(letter in front_vowels for letter in word)]
# back_harmony_words = [word for word in words if all(letter in back_vowels for letter in word)]

# create a DataFrame to hold the counts of each consonant in front and back harmony words
consonants = list([c for word in words for c in word if c not in front_vowels + mid_vowels + back_vowels])
consonant_counts = pd.DataFrame(index=['Front', 'Back'], columns=consonants, dtype=int).fillna(0)

# iterate over each word and increment the count for each consonant in the appropriate row
for word in front_harmony_words:
    for consonant in consonants:
        if consonant in word:
            consonant_counts.at['Front', consonant] += 1

for word in back_harmony_words:
    for consonant in consonants:
        if consonant in word:
            consonant_counts.at['Back', consonant] += 1

alpha = 0.05
n_tests = len(consonants)

# perform chi-square tests for each consonant
for consonant in consonants:
    obs = consonant_counts.loc[:, consonant].values.reshape(2, 1)
    chi2, p, dof, expected = chi2_contingency(obs)
    print(f"Consonant statistics for: {consonant}")
    print(f"Observed counts: {obs.ravel()}")
    print(f"Expected counts: {expected.ravel()}")
    print(f"Chi-square statistic: {chi2}")
    print(f"P-value: {p}\n")
    print("Without Bonferri correction:")
    if p < alpha:
        print("The counts are dependent.\n")
    else:
        print("The counts are independent.\n")

    # perform Bonferroni correction
    print("With Bonferroni correction:")
    if p < alpha / n_tests:
        print("The counts are dependent.\n")
    else:
        print("The counts are independent.\n")

