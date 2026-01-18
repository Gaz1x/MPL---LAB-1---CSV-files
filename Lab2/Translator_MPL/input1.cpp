#include <iostream>
using namespace std;

void analyzeNumberProperties(int n) {
    cout << "Analyzing number: " << n << endl;
    if (n <= 0) {
        cout << "Only positive integers are analyzed." << endl;
        return;
    }
    int sum = 0;
    int divisorCount = 0;
    int evenDivisors = 0;
    int oddDivisors = 0;
    int primeDivisors = 0;
    cout << "Finding all proper divisors of " << n << "..." << endl;
    for (int i = 1; i < n; i++) {
        if (n % i == 0) {
            sum += i;
            divisorCount++;
            cout << "Found divisor: " << i << endl;
            if (i % 2 == 0) {
                evenDivisors++;
            } else {
                oddDivisors++;
            }
            bool isPrime = true;
            if (i < 2) {
                isPrime = false;
            } else {
                for (int j = 2; j * j <= i; j++) {
                    if (i % j == 0) {
                        isPrime = false;
                        break;
                    }
                }
            }
            if (isPrime) {
                primeDivisors++;
                cout << "  -> " << i << " is a prime divisor." << endl;
            }
        }
    }
    cout << "=== SUMMARY ===" << endl;
    cout << "Sum of proper divisors: " << sum << endl;
    cout << "Total divisors: " << divisorCount << endl;
    cout << "Even divisors: " << evenDivisors << endl;
    cout << "Odd divisors: " << oddDivisors << endl;
    cout << "Prime divisors: " << primeDivisors << endl;
    if (sum == n) {
        cout << n << " is a PERFECT number!" << endl;
    } else if (sum > n) {
        cout << n << " is an ABUNDANT number." << endl;
    } else {
        cout << n << " is a DEFICIENT number." << endl;
    }
    if (divisorCount == 1 && n > 1) {
        cout << n << " is also a PRIME number." << endl;
    }
    cout << "Analysis complete for " << n << "." << endl;
}