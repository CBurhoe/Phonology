import pandas as pd
from scipy.stats import chi2_contingency
import numpy as np

pd.set_option('display.max_columns', None)

# define front, mid, and back vowels
front_vowels = {'ø', 'æ', 'y'}
mid_vowels = {'e', 'i'}
back_vowels = {'ɑ', 'o', 'u'}
all_vowels = front_vowels | mid_vowels | back_vowels
consonants = ['d', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'š', 'f', 'b']


# read in the word list and categorize each word based on vowel harmony
words = []
categories = []
with open('preprocessed-index.txt', 'r', encoding='utf-8') as f:
    for word in f.readlines():
        word = word.strip()
        front = False
        back = False
        neutral = False
        discard = False
        for letter in word:
            if letter in front_vowels:
                front = True
                back = False
            elif letter in mid_vowels:
                neutral = True
            elif letter in back_vowels:
                back = True
                front = False
            elif (letter not in consonants) & (letter not in all_vowels):
                discard = True
        if discard:
            category = 'Unknown'
        elif front:
            category = 'Front'
        elif back:
            category = 'Back'
        elif neutral:
            category = 'Front'
        else:
            category = 'Unknown'
        words.append(word)
        categories.append(category)

# write out unknown words to a file
with open('unknown-words.txt', 'w', encoding='utf-8') as f:
    for word, category in zip(words, categories):
        if category == 'Unknown':
            f.write(word + '\n')
f.close()

# create a DataFrame to hold the word list and categories
df = pd.DataFrame({'Word': words, 'Vowel Harmony': categories})

# create lists of front and back harmony words
front_harmony_words = df[df['Vowel Harmony'] == 'Front']['Word'].tolist()
back_harmony_words = df[df['Vowel Harmony'] == 'Back']['Word'].tolist()

# print out summary statistics
print('Number of usable words:', len(front_harmony_words) + len(back_harmony_words))
print('Number of front-harmony words:', len(df[df['Vowel Harmony'] == 'Front']))
print('Number of back-harmony words:', len(df[df['Vowel Harmony'] == 'Back']))
print('Number of discarded words:', len(df[df['Vowel Harmony'] == 'Unknown']))

# create a DataFrame to hold the counts of each initial consonant in front and back harmony words
initial_phoneme_contingency = pd.DataFrame(index=['Front', 'Back'], columns=consonants + ['vowel'], dtype=int).fillna(0)

# iterate over each word and increment the count for the corresponding initial phoneme
for word in front_harmony_words:
    if word[0] in consonants:
        for consonant in set(consonants):
            if consonant == word[0]:
                initial_phoneme_contingency.at['Front', consonant] += 1
    else:
        initial_phoneme_contingency.at['Front', 'vowel'] += 1

for word in back_harmony_words:
    if word[0] in consonants:
        for consonant in set(consonants):
            if consonant == word[0]:
                initial_phoneme_contingency.at['Back', consonant] += 1
    else:
        initial_phoneme_contingency.at['Back', 'vowel'] += 1

alpha = 0.05

# # perform chi-square test for all word initials
chi2_stat, p_val, dof, expected = chi2_contingency(initial_phoneme_contingency, correction=True)

# print the results
print(f'Chi-square statistic: {chi2_stat}')
print(f'p-value: {p_val}')
print(f'Degrees of freedom: {dof}')

# perform hypothesis test with p value.
if p_val < alpha:
    print("The counts are dependent.\n")
    print("Need to determine where the dependency lies.\n")
else:
    print("The counts are independent.\n")

# determine the contributions to the overall chi-square statistic
contributions = (initial_phoneme_contingency - expected)**2 / expected
max_contributions = contributions.values.max()
max_contributions_cells = list(zip(*np.where(contributions.values == max_contributions)))

# print the contributions
print('Observed values:')
print(initial_phoneme_contingency)
print('Expected values:')
for row in expected:
    for value in row:
        print(f"{value:.2f} ", end='')
    print()
print('Contributions to Chi-square statistic:')
print(contributions)
print(f'Largest contribution: {max_contributions}')
print('Cells with largest contribution:')
for cell in max_contributions_cells:
    print(initial_phoneme_contingency.index[cell[0]], initial_phoneme_contingency.columns[cell[1]])

# print out frequencies of each initial consonant
front_freqs = initial_phoneme_contingency.loc['Front', :].drop('vowel').sort_values(ascending=False)
back_freqs = initial_phoneme_contingency.loc['Back', :].drop('vowel').sort_values(ascending=False)

print('Front harmony | Back harmony')
print(f"{front_freqs.index[0]} ({front_freqs.iloc[0]})  | {back_freqs.index[0]} ({back_freqs.iloc[0]})")
for i in range(1, len(front_freqs)):
    print(f"{front_freqs.index[i]} ({front_freqs.iloc[i]})  | {back_freqs.index[i]} ({back_freqs.iloc[i]})")

# print out probability masses of each initial consonant
# calculate and print probability mass of each initial character for front and back harmony words
front_prob_mass = initial_phoneme_contingency.loc['Front', :].div(initial_phoneme_contingency.loc['Front', :].sum())
back_prob_mass = initial_phoneme_contingency.loc['Back', :].div(initial_phoneme_contingency.loc['Back', :].sum())

print('Initial character probability mass for front and back harmony words:')
print('Front harmony | Back harmony')
for front_char, back_char in zip(front_prob_mass.sort_values(ascending=False).items(), back_prob_mass.sort_values(ascending=False).items()):
    print(f"{front_char[0]}: {front_char[1]:.4f} | {back_char[0]}: {back_char[1]:.4f}")


# perform testing above using random sampling on each harmony group to get equal sample sizes
print("Results from random sampling:")
samples_with_significant_results = 0
f = open('random_sampling_results.txt', 'w', encoding='utf-8')
for i in range(10):
    # take samples of front and back harmony words
    front_sample = df[df['Vowel Harmony'] == 'Front']['Word'].sample(n=6000).tolist()
    back_sample = df[df['Vowel Harmony'] == 'Back']['Word'].sample(n=6000).tolist()
    # create a DataFrame to hold the counts of each initial consonant in front and back harmony words
    initial_phoneme_contingency = pd.DataFrame(index=['Front', 'Back'], columns=consonants + ['vowel'],
                                               dtype=int).fillna(0)

    # iterate over each word and increment the count for the corresponding initial phoneme
    for word in front_sample:
        if word[0] in consonants:
            for consonant in set(consonants):
                if consonant == word[0]:
                    initial_phoneme_contingency.at['Front', consonant] += 1
        else:
            initial_phoneme_contingency.at['Front', 'vowel'] += 1

    for word in back_sample:
        if word[0] in consonants:
            for consonant in set(consonants):
                if consonant == word[0]:
                    initial_phoneme_contingency.at['Back', consonant] += 1
        else:
            initial_phoneme_contingency.at['Back', 'vowel'] += 1

    alpha = 0.05

    # # perform chi-square test for all word initials
    chi2_stat, p_val, dof, expected = chi2_contingency(initial_phoneme_contingency, correction=True)

    if p_val < alpha:
        samples_with_significant_results += 1
    # determine the contributions to the overall chi-square statistic
    contributions = (initial_phoneme_contingency - expected) ** 2 / expected
    max_contributions = contributions.values.max()
    max_contributions_cells = list(zip(*np.where(contributions.values == max_contributions)))

    f.write('Observed values:\n')
    f.write(initial_phoneme_contingency.to_string())
    f.write('\n')
    f.write("Expected values:\n")
    for row in expected:
        for value in row:
            f.write(f"{value:.2f} ")
        f.write('\n')
    f.write('\n')
    f.write('Contributions to Chi-square statistic:\n')
    f.write(contributions.to_string())
    f.write('\n')
    f.write(f'Largest contribution: {max_contributions}\n')
    f.write('Cells with largest contribution:\n')
    for cell in max_contributions_cells:
        f.write(initial_phoneme_contingency.index[cell[0]])
        f.write(' ')
        f.write(initial_phoneme_contingency.columns[cell[1]])
        f.write('\n')

    # print out frequencies of each initial consonant
    front_freqs = initial_phoneme_contingency.loc['Front', :].drop('vowel').sort_values(ascending=False)
    back_freqs = initial_phoneme_contingency.loc['Back', :].drop('vowel').sort_values(ascending=False)

    f.write('Front harmony | Back harmony\n')
    f.write(f"{front_freqs.index[0]} ({front_freqs.iloc[0]})  | {back_freqs.index[0]} ({back_freqs.iloc[0]})\n")
    for i in range(1, len(front_freqs)):
        f.write(f"{front_freqs.index[i]} ({front_freqs.iloc[i]})  | {back_freqs.index[i]} ({back_freqs.iloc[i]})\n")

        # f.write out probability masses of each initial consonant
        # calculate and f.write probability mass of each initial character for front and back harmony words
        # front_prob_mass = initial_phoneme_contingency.loc['Front', :].div(
        #     initial_phoneme_contingency.loc['Front', :].sum())
        # back_prob_mass = initial_phoneme_contingency.loc['Back', :].div(
        #     initial_phoneme_contingency.loc['Back', :].sum())
        #
        # f.write('Initial character probability mass for front and back harmony words:\n')
        # f.write('Front harmony | Back harmony\n')
        # for front_char, back_char in zip(front_prob_mass.sort_values(ascending=False).items(),
        #                                  back_prob_mass.sort_values(ascending=False).items()):
        #     f.write(f"{front_char[0]}: {front_char[1]:.4f} | {back_char[0]}: {back_char[1]:.4f}\n")
f.close()
print(f"Number of samples with significant results: {samples_with_significant_results}")
print("See random_sampling_results.txt for results from random sampling.")


# perform chi-square tests for each consonant
# for consonant in consonants:
#     obs = consonant_counts.loc[:, consonant].values.reshape(2, 1)
#     print("Observed values:", obs)
#
#     chi2, p, dof, expected = chi2_contingency(obs)
#     print(f"Consonant statistics for: {consonant}")
#     print(f"Observed counts: {obs.ravel()}")
#     print(f"Expected counts: {expected.ravel()}")
#     print(f"Chi-square statistic: {chi2}")
#     print(f"P-value: {p}\n")
#
#     # perform hypothesis test without Bonferroni correction
#     if p < alpha:
#         print("The counts are dependent (without Bonferroni correction).\n")
#     else:
#         print("The counts are independent (without Bonferroni correction).\n")
#
#     # perform hypothesis test with Bonferroni correction
#     if p < alpha / n_tests:
#         print("The counts are dependent (with Bonferroni correction).\n")
#     else:
#         print("The counts are independent (with Bonferroni correction).\n")
