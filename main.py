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
  if n < 20: return double_digit[n - 10]
  if n < 100: return f"{below_hundred[(n - (n % 10)) / 10 - 2]} {spell_number(n % 10)}"
  if n < 1000: return f"{single_digit[n / 100]} {hundred} {spell_number(n % 100)}"
  if n < 1000000: return f"{spell_number(n / 1000)} {thousand} {spell_number(n % 1000)}"
  if n < 1000000000: return f"{spell_number(n / 1000000)} {million} {spell_number(n % 1000000)}"
  return f"{spell_number(n / 1000000000)} {billion} ${spell_number(n % 1000000000)}"

def spell_char(c: str, n: int) -> str:
  return f"{spell_number(n)} ❛{c}❜s"

type CharCounts = list[(str, int)]

def spell_chars(chars: CharCounts) -> str:
  spelled = [spell_char(c, n) if n > 0 else "" for (c, n) in chars]
  [*parts, last] = spelled if len(spelled) > 0 else [""]
  return f"{", ".join(parts)} and {last}"

def spell_instructions(chars: CharCounts) -> str:
  return f"With that - please write down {spell_chars(chars)}, in a palindromic sequence whose second half runs thus:"

def spell_output(prefix: str, chars: CharCounts) -> str:
  start = f"{prefix} {spell_instructions(chars)}"
  return f"{start}\n{start[::-1]}"

type Alphabet = list[str]

def get_alphabet(prefix: str) -> Alphabet:
  return sorted(list(set(
    "".join(single_digit + double_digit + below_hundred) 
      + hundred 
      + thousand 
      + million 
      + billion 
      + spell_char('', 0)
      + spell_chars([])
      + spell_instructions([])
      + prefix
    ) - set(' ')))

def alphabet_to_dict(alphabet: Alphabet) -> dict[str, int]:
  return {k: v for (v, k) in enumerate(alphabet)}

def count_chars(s: str) -> CharCounts:
  counts = {}
  for c in "".join(s.split()):
    counts[c] = 1 + counts.get(c, 0)
  return counts

type Vector = list[int]

def get_base_vector(prefix: str) -> Vector:
  alphabet = get_alphabet(prefix)
  alphabet_dict = alphabet_to_dict(alphabet)

  base_vector = [0] * len(alphabet)
  minimal_message = count_chars(spell_output(prefix, []))
  for k, v in minimal_message.items():
    base_vector[alphabet_dict[k]] = v

  return base_vector

print(f"Alphabet: {get_alphabet("Alphabet:")}")
print(get_base_vector("Alphabet:"))
print(spell_output("Alphabet:", []))
