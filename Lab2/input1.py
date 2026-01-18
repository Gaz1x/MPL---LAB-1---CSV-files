def analyzeNumberProperties(n):
    print("Analyzing number: ", n)
    if n <= 0:
        print("Only positive integers are analyzed.")
        return
    sum = 0
    divisorCount = 0
    evenDivisors = 0
    oddDivisors = 0
    primeDivisors = 0
    print("Finding all proper divisors of ", n, "...")
    for i in range(1, n):
        if n % i == 0:
            sum += i
            divisorCount += 1
            print("Found divisor: ", i)
            if i % 2 == 0:
                evenDivisors += 1
            else:
                oddDivisors += 1
            isPrime = True
            if i < 2:
                isPrime = False
            else:
                for j in range(2, int(i ** 0.5) + 1):
                    if i % j == 0:
                        isPrime = False
                        break
            if isPrime:
                primeDivisors += 1
                print("  -> ", i, " is a prime divisor.")
    print("=== SUMMARY ===")
    print("Sum of proper divisors: ", sum)
    print("Total divisors: ", divisorCount)
    print("Even divisors: ", evenDivisors)
    print("Odd divisors: ", oddDivisors)
    print("Prime divisors: ", primeDivisors)
    if sum == n:
        print(n, " is a PERFECT number!")
    elif sum > n:
        print(n, " is an ABUNDANT number.")
    else:
        print(n, " is a DEFICIENT number.")
    if divisorCount == 1 and n > 1:
        print(n, " is also a PRIME number.")
