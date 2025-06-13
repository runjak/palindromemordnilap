single_digit = [
  "",
  "one",
  "two",
  "three",
  "four",
  "five",
  "six",
  "seven",
  "eight",
  "nine",
]

double_digit = [
  "ten",
  "eleven",
  "twelve",
  "thirteen",
  "fourteen",
  "fifteen",
  "sixteen",
  "seventeen",
  "eighteen",
  "nineteen",
]

below_hundred = [
  "twenty",
  "thirty",
  "forty",
  "fifty",
  "sixty",
  "seventy",
  "eighty",
  "ninety",
]

hundred = "hundred"
thousand = "thousand"
million = "million"
billion = "billion"

def spell_number(n: int) -> str:
  if n <= 0: return ''
  if n < 10: return single_digit[n]
  if n < 20: return double_digit[n-10]
  if n < 100: return f"{below_hundred[(n - (n%10)) / 10 - 2]} {spell_number(n%10)}"
  if n < 1000: return f"{single_digit[n/100]} {hundred} {spell_number(n%100)}"
  if n < 1000000: return f"{spell_number(n / 1000)} {thousand} {spell_number(n % 1000)}"
  if n < 1000000000: return f"{spell_number(n / 1000000)} {million} {spell_number(n % 1000000)}"
  return f"{spell_number(n / 1000000000)} {billion} ${spell_number(n % 1000000000)}"

def spell_char(c: str, n: int) -> str:
  return f"{spell_number(n)} ❛{c}❜s"

alphabet = sorted(list(set(
  "".join(single_digit + double_digit + below_hundred) 
    + hundred 
    + thousand 
    + million 
    + billion 
    + spell_char('', 0)
  ) - set(' ')))

print(f"Alphabet: {alphabet}")