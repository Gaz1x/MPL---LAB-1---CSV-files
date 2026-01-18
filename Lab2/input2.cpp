#include <iostream>
using namespace std;

void analyzeStringBalance(char text[], int len) {
    cout << "Analyzing string of length " << len << "..." << endl;
    int vowelCount = 0;
    int consonantCount = 0;
    int spaceCount = 0;
    int digitCount = 0;
    int otherCount = 0;
    int letterFreq[26] = {0};
    cout << "Processing each character:" << endl;
    for (int i = 0; i < len; i++) {
        char c = text[i];
        cout << "Char [" << i << "] = '" << c << "'" << endl;
        if (c >= 'A' && c <= 'Z') {
            c = c - 'A' + 'a';
        }
        if (c >= 'a' && c <= 'z') {
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
                vowelCount++;
                cout << "  -> Vowel found." << endl;
            } else {
                consonantCount++;
                cout << "  -> Consonant found." << endl;
            }
            letterFreq[c - 'a']++;
        } else if (c == ' ') {
            spaceCount++;
        } else if (c >= '0' && c <= '9') {
            digitCount++;
        } else {
            otherCount++;
        }
    }
    cout << "=== LETTER FREQUENCY ===" << endl;
    int uniqueLetters = 0;
    for (int i = 0; i < 26; i++) {
        if (letterFreq[i] > 0) {
            uniqueLetters++;
            cout << (char)('a' + i) << ": " << letterFreq[i] << endl;
        }
    }
    cout << "=== STATISTICS ===" << endl;
    cout << "Vowels: " << vowelCount << endl;
    cout << "Consonants: " << consonantCount << endl;
    cout << "Spaces: " << spaceCount << endl;
    cout << "Digits: " << digitCount << endl;
    cout << "Other symbols: " << otherCount << endl;
    cout << "Unique letters used: " << uniqueLetters << endl;
    if (vowelCount == consonantCount && vowelCount > 0) {
        cout << "The string is BALANCED (vowels == consonants)!" << endl;
    } else {
        cout << "The string is NOT balanced." << endl;
    }
    cout << "String analysis complete." << endl;
}