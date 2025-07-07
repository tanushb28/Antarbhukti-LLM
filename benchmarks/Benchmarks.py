sfc_examples = [
# 1. Sum of first n natural numbers
{
    "steps": [
        {"name": "Init", "function": "sum := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Add", "function": "sum := sum + i"},
        {"name": "Inc", "function": "i := i + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Add", "guard": "i <= n"},
        {"src": "Add", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["i", "sum", "n", "init"]
},
# 2. Fibonacci n-th term (scalar)
{
    "steps": [
        {"name": "Init", "function": "a := 0; b := 1; count := 2"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "temp := a + b; a := b; b := temp"},
        {"name": "Inc", "function": "count := count + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "count <= n"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "count > n"}
    ],
    "variables": ["a", "b", "temp", "count", "n", "init"]
},
# 3. GCD (Euclidean algorithm)
{
    "steps": [
        {"name": "Start", "function": "x := a; y := b"},
        {"name": "Check", "function": ""},
        {"name": "Swap", "function": "temp := x; x := y; y := temp % y"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Start", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Swap", "guard": "y != 0"},
        {"src": "Swap", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "y == 0"}
    ],
    "variables": ["x", "y", "temp", "a", "b", "init"]
},
# 4. LCM using GCD
{
    "steps": [
        {"name": "Init", "function": "gcd := 1; prod := a*b"},
        {"name": "GCDStart", "function": "x := a; y := b"},
        {"name": "GCDCheck", "function": ""},
        {"name": "GCDStep", "function": "temp := x; x := y; y := temp % y"},
        {"name": "LCMEnd", "function": "lcm := prod // x"}
    ],
    "transitions": [
        {"src": "Init", "tgt": "GCDStart", "guard": "init"},
        {"src": "GCDStart", "tgt": "GCDCheck", "guard": "True"},
        {"src": "GCDCheck", "tgt": "GCDStep", "guard": "y != 0"},
        {"src": "GCDStep", "tgt": "GCDCheck", "guard": "True"},
        {"src": "GCDCheck", "tgt": "LCMEnd", "guard": "y == 0"}
    ],
    "variables": ["x", "y", "temp", "a", "b", "gcd", "prod", "lcm", "init"]
},
# 5. Reverse a number
{
    "steps": [
        {"name": "Init", "function": "rev := 0; num := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "rev := rev*10 + num%10; num := num//10"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["rev", "num", "n", "init"]
},
# 6. Count digits in a number
{
    "steps": [
        {"name": "Init", "function": "num := n; count := 0"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "num := num//10; count := count+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["num", "count", "n", "init"]
},
# 7. Power (x^y)
{
    "steps": [
        {"name": "Init", "function": "res := 1; cnt := 0"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "res := res * x; cnt := cnt + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "cnt < y"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "cnt >= y"}
    ],
    "variables": ["x", "y", "res", "cnt", "init"]
},
# 8. Sum of digits
{
    "steps": [
        {"name": "Init", "function": "s := 0; num := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "s := s + num%10; num := num//10"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["s", "num", "n", "init"]
},
# 9. Palindrome check (number)
{
    "steps": [
        {"name": "Init", "function": "rev := 0; num := n; orig := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "rev := rev*10 + num%10; num := num//10"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["rev", "num", "orig", "n", "init"]
},
# 10. Armstrong number check (3-digit)
{
    "steps": [
        {"name": "Init", "function": "num := n; sum := 0"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "d := num % 10; sum := sum + d*d*d; num := num // 10"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["d", "sum", "num", "n", "init"]
},
# 11. Prime number check
{
    "steps": [
        {"name": "Init", "function": "i := 2; is_prime := True"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "is_prime := is_prime and (n % i != 0)"},
        {"name": "Inc", "function": "i := i + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "i*i <= n and is_prime"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "not is_prime or i*i > n"}
    ],
    "variables": ["i", "is_prime", "n", "init"]
},
# 12. Next prime after n
{
    "steps": [
        {"name": "Init", "function": "num := n+1"},
        {"name": "PrimeCheck", "function": "i := 2; is_prime := True"},
        {"name": "InnerCheck", "function": ""},
        {"name": "Step", "function": "is_prime := is_prime and (num % i != 0)"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "NextNum", "function": "num := num+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "PrimeCheck", "guard": "init"},
        {"src": "PrimeCheck", "tgt": "InnerCheck", "guard": "True"},
        {"src": "InnerCheck", "tgt": "Step", "guard": "i*i <= num and is_prime"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "InnerCheck", "guard": "True"},
        {"src": "InnerCheck", "tgt": "End", "guard": "is_prime and i*i > num"},
        {"src": "InnerCheck", "tgt": "NextNum", "guard": "not is_prime"},
        {"src": "NextNum", "tgt": "PrimeCheck", "guard": "True"}
    ],
    "variables": ["num", "i", "is_prime", "n", "init"]
},
# 13. Factorial (classic)
{
    "steps": [
        {"name": "Start", "function": "i := 1; fact := 1"},
        {"name": "Check", "function": ""},
        {"name": "Multiply", "function": "fact := fact * i"},
        {"name": "Increment", "function": "i := i + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Start", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},
        {"src": "Multiply", "tgt": "Increment", "guard": "True"},
        {"src": "Increment", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["i", "fact", "n", "init"]
},
# 14. Product of first n numbers
{
    "steps": [
        {"name": "Init", "function": "prod := 1; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "prod := prod * i"},
        {"name": "Inc", "function": "i := i + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "i <= n"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["i", "prod", "n", "init"]
},
# 15. Count trailing zeros in n!
{
    "steps": [
        {"name": "Init", "function": "cnt := 0; i := 5"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "cnt := cnt + n//i; i := i*5"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "i <= n"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["cnt", "i", "n", "init"]
},
# 16. Integer square root (by subtraction)
{
    "steps": [
        {"name": "Init", "function": "i := 1; n1 := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "n1 := n1 - i; i := i + 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "n1 >= i"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "n1 < i"}
    ],
    "variables": ["i", "n1", "n", "init"]
},
# 17. Integer log base 2
{
    "steps": [
        {"name": "Init", "function": "cnt := 0; num := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "num := num // 2; cnt := cnt + 1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 1"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num <= 1"}
    ],
    "variables": ["cnt", "num", "n", "init"]
},
# 18. HCF by subtraction
{
    "steps": [
        {"name": "Init", "function": "x := a; y := b"},
        {"name": "Check", "function": ""},
        {"name": "StepX", "function": "x := x - y"},
        {"name": "StepY", "function": "y := y - x"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "StepX", "guard": "x > y"},
        {"src": "Check", "tgt": "StepY", "guard": "y > x"},
        {"src": "Check", "tgt": "End", "guard": "x == y"},
        {"src": "StepX", "tgt": "Check", "guard": "True"},
        {"src": "StepY", "tgt": "Check", "guard": "True"}
    ],
    "variables": ["x", "y", "a", "b", "init"]
},
# 19. Sum of squares up to n
{
    "steps": [
        {"name": "Init", "function": "sum := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "sum := sum + i*i"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "i <= n"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["sum", "i", "n", "init"]
},
# 20. Sum of cubes up to n
{
    "steps": [
        {"name": "Init", "function": "sum := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "sum := sum + i*i*i"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "i <= n"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["sum", "i", "n", "init"]
},
# 21. Digital root
{
    "steps": [
        {"name": "Init", "function": "num := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "s := 0"},
        {"name": "SumDigits", "function": "s := s + num%10; num := num//10"},
        {"name": "LoopCheck", "function": ""},
        {"name": "Recur", "function": "num := s"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num >= 10"},
        {"src": "Step", "tgt": "SumDigits", "guard": "num > 0"},
        {"src": "SumDigits", "tgt": "Step", "guard": "num > 0"},
        {"src": "SumDigits", "tgt": "LoopCheck", "guard": "num == 0"},
        {"src": "LoopCheck", "tgt": "Recur", "guard": "s >= 10"},
        {"src": "LoopCheck", "tgt": "End", "guard": "s < 10"},
        {"src": "Check", "tgt": "End", "guard": "num < 10"}
    ],
    "variables": ["num", "s", "n", "init"]
},
# 22. Digital product until single digit
{
    "steps": [
        {"name": "Init", "function": "num := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "p := 1"},
        {"name": "MultDigits", "function": "p := p * (num%10); num := num//10"},
        {"name": "LoopCheck", "function": ""},
        {"name": "Recur", "function": "num := p"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num >= 10"},
        {"src": "Step", "tgt": "MultDigits", "guard": "num > 0"},
        {"src": "MultDigits", "tgt": "Step", "guard": "num > 0"},
        {"src": "MultDigits", "tgt": "LoopCheck", "guard": "num == 0"},
        {"src": "LoopCheck", "tgt": "Recur", "guard": "p >= 10"},
        {"src": "LoopCheck", "tgt": "End", "guard": "p < 10"},
        {"src": "Check", "tgt": "End", "guard": "num < 10"}
    ],
    "variables": ["num", "p", "n", "init"]
},
# 23. Nth triangular number
{
    "steps": [
        {"name": "Init", "function": "tri := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Add", "function": "tri := tri + i"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Add", "guard": "i <= n"},
        {"src": "Add", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["tri", "i", "n", "init"]
},
# 24. Nth pentagonal number
{
    "steps": [
        {"name": "Init", "function": "pent := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Add", "function": "pent := pent + (3*i-2)"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Add", "guard": "i <= n"},
        {"src": "Add", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["pent", "i", "n", "init"]
},
# 25. Nth Pell number
{
    "steps": [
        {"name": "Init", "function": "a := 0; b := 1; i := 2"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "temp := b; b := 2*b + a; a := temp"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "i <= n"},
        {"src": "Step", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["a", "b", "temp", "i", "n", "init"]
},
# 26. Check number is even
{
    "steps": [
        {"name": "Init", "function": "even := (n % 2 == 0)"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["even", "n", "init"]
},
# 27. Check number is odd
{
    "steps": [
        {"name": "Init", "function": "odd := (n % 2 != 0)"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["odd", "n", "init"]
},
# 28. Check leap year
{
    "steps": [
        {"name": "Init", "function": "leap := ((n % 4 == 0 and n % 100 != 0) or (n % 400 == 0))"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["leap", "n", "init"]
},
# 29. Test divisibility by 3
{
    "steps": [
        {"name": "Init", "function": "div3 := (n % 3 == 0)"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["div3", "n", "init"]
},
# 30. Test divisibility by 5
{
    "steps": [
        {"name": "Init", "function": "div5 := (n % 5 == 0)"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["div5", "n", "init"]
},
# 31. Next even number after n
{
    "steps": [
        {"name": "Init", "function": "next_even := n + 1 if n % 2 != 0 else n + 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["next_even", "n", "init"]
},
# 32. Next odd number after n
{
    "steps": [
        {"name": "Init", "function": "next_odd := n + 1 if n % 2 == 0 else n + 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["next_odd", "n", "init"]
},
# 33. Sum of odd numbers up to n
{
    "steps": [
        {"name": "Init", "function": "sum := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "Add", "function": "sum := sum + i"},
        {"name": "Inc", "function": "i := i + 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Add", "guard": "i <= n"},
        {"src": "Add", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["i", "sum", "n", "init"]
},
# 34. Sum of even numbers up to n
{
    "steps": [
        {"name": "Init", "function": "sum := 0; i := 2"},
        {"name": "Check", "function": ""},
        {"name": "Add", "function": "sum := sum + i"},
        {"name": "Inc", "function": "i := i + 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Add", "guard": "i <= n"},
        {"src": "Add", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ],
    "variables": ["i", "sum", "n", "init"]
},
# 35. Double a number n
{
    "steps": [
        {"name": "Init", "function": "doubled := n * 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["doubled", "n", "init"]
},
# 36. Halve a number n (integer division)
{
    "steps": [
        {"name": "Init", "function": "halved := n // 2"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["halved", "n", "init"]
},
# 37. Check perfect number
{
    "steps": [
        {"name": "Init", "function": "sum := 0; i := 1"},
        {"name": "Check", "function": ""},
        {"name": "DivAdd", "function": "sum := sum + i"},
        {"name": "Inc", "function": "i := i+1"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "DivAdd", "guard": "i < n and n % i == 0"},
        {"src": "Check", "tgt": "Inc", "guard": "i < n and n % i != 0"},
        {"src": "DivAdd", "tgt": "Inc", "guard": "True"},
        {"src": "Inc", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i >= n"}
    ],
    "variables": ["sum", "i", "n", "init"]
},
# 38. Check Harshad number
{
    "steps": [
        {"name": "Init", "function": "num := n; s := 0"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "s := s + num%10; num := num//10"},
        {"name": "End", "function": "harshad := (n % s == 0)"}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["num", "s", "harshad", "n", "init"]
},
# 39. Check palindrome for integer n (copy of #9, for completeness)
{
    "steps": [
        {"name": "Init", "function": "rev := 0; num := n; orig := n"},
        {"name": "Check", "function": ""},
        {"name": "Step", "function": "rev := rev*10 + num%10; num := num//10"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Step", "guard": "num > 0"},
        {"src": "Step", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "num == 0"}
    ],
    "variables": ["rev", "num", "orig", "n", "init"]
},
# 40. Add two numbers
{
    "steps": [
        {"name": "Init", "function": "sum := a + b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["sum", "a", "b", "init"]
},
# 41. Subtract two numbers
{
    "steps": [
        {"name": "Init", "function": "diff := a - b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["diff", "a", "b", "init"]
},
# 42. Multiply two numbers
{
    "steps": [
        {"name": "Init", "function": "prod := a * b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["prod", "a", "b", "init"]
},
# 43. Integer division of two numbers
{
    "steps": [
        {"name": "Init", "function": "quot := a // b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["quot", "a", "b", "init"]
},
# 44. Remainder of two numbers
{
    "steps": [
        {"name": "Init", "function": "rem := a % b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["rem", "a", "b", "init"]
},
# 45. Maximum of two numbers
{
    "steps": [
        {"name": "Init", "function": "mx := a if a > b else b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["mx", "a", "b", "init"]
},
# 46. Minimum of two numbers
{
    "steps": [
        {"name": "Init", "function": "mn := a if a < b else b"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["mn", "a", "b", "init"]
},
# 47. Swap two numbers
{
    "steps": [
        {"name": "Init", "function": "temp := a; a := b; b := temp"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["temp", "a", "b", "init"]
},
# 48. Celsius to Fahrenheit
{
    "steps": [
        {"name": "Init", "function": "f := c * 9 / 5 + 32"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["f", "c", "init"]
},
# 49. Fahrenheit to Celsius
{
    "steps": [
        {"name": "Init", "function": "c := (f - 32) * 5 / 9"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["c", "f", "init"]
},
# 50. Absolute value of n
{
    "steps": [
        {"name": "Init", "function": "absn := n if n >= 0 else -n"},
        {"name": "End", "function": ""}
    ],
    "transitions": [
        {"src": "Init", "tgt": "End", "guard": "init"}
    ],
    "variables": ["absn", "n", "init"]
},
]

# To print a sample as SFC code:
for idx, sfc in enumerate(sfc_examples, 1):
    print(f"# --- SFC Example {idx} ---")
    print(f"steps = {sfc['steps']}")
    print(f"transitions = {sfc['transitions']}")
    print(f"variables = {sfc['variables']}\n")