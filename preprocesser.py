import codecs

# Open input and output files using UTF-8 encoding
with codecs.open('index.noun', 'r', encoding='utf-8') as f_in, codecs.open('preprocessed-index.noun', 'w', encoding='utf-8') as f_out:
    # Skip first 29 lines
    for i in range(29):
        next(f_in)
    word_count = 0
    # Process each line
    for line in f_in:
        # Split the line into words
        words = line.split()

        # If the first word is a single character, skip the line
        if len(words[0]) == 1:
            continue
        word_count += 1
        # Otherwise, write the first word to the output file
        f_out.write(words[0] + '\n')
    print(word_count, "words written to preprocessed-index.txt")
f_in.close()
f_out.close()

    # replace instances of 'ö' and 'ä' with 'ø' and 'æ' respectively
with open('preprocessed-index.noun', 'r', encoding='utf-8') as f_in, open('preprocessed-index.txt', 'w', encoding='utf-8') as f_out:
    for line in f_in:
        f_out.write(line.replace('ö', 'ø').replace('ä', 'æ').replace('a', 'ɑ'))
f_in.close()
f_out.close()