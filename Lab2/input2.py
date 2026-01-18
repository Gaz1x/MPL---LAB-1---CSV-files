def analyzeStringBalance(text, len):
    print("Analyzing string of length ", len, "...")
    vowelCount = 0
    consonantCount = 0
    spaceCount = 0
    digitCount = 0
    otherCount = 0
    letterFreq = [0] * 26
    print("Processing each character:")
    for i in range(0, len):
        c = text = [0] * i
        print("Char [", i, "] = '", c, "'")
        if c >= 'A' and c <= 'Z':
            c = chr(ord('A') + 'a')
        if c >= 'a' and c <= 'z':
            if c == 'a' or c == 'e' or c == 'i' or c == 'o' or c == 'u':
                vowelCount += 1
                print("  -> Vowel found.")
            else:
                consonantCount += 1
                print("  -> Consonant found.")
            letterFreq[ord(c) - ord('a')] += 1
        elif c == ' ':
            spaceCount += 1
        elif c >= '0' and c <= '9':
            digitCount += 1
        else:
            otherCount += 1
    print("=== LETTER FREQUENCY ===")
    uniqueLetters = 0
    for i in range(0, 26):
        if letterFreq[i] > 0:
            uniqueLetters += 1
            print(chr(ord('a') + i), ": ", letterFreq[i])
    print("=== STATISTICS ===")
    print("Vowels: ", vowelCount)
    print("Consonants: ", consonantCount)
    print("Spaces: ", spaceCount)
    print("Digits: ", digitCount)
    print("Other symbols: ", otherCount)
    print("Unique letters used: ", uniqueLetters)
    if vowelCount == consonantCount and vowelCount > 0:
        print("The string is BALANCED (vowels == consonants)!")
    else:
        print("The string is NOT balanced.")
    print("String analysis complete.")
