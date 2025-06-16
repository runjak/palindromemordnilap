type Vector = dict[str, int]
type Alphabet = list[str]

known_text = "\n".join([
  "*",
  "Write",
  "down ten ❛a❜s,",
  "eight ❛c❜s, ten ❛d❜s,",
  "fifty-two ❛e❜s, thirty-eight ❛f❜s,",
  "sixteen ❛g❜s, thirty ❛h❜s, forty-eight ❛i❜s,",
  "six ❛l❜s, four ❛m❜s, thirty-two ❛n❜s, forty-four ❛o❜s,",
  "four ❛p❜s, four ❛q❜s, forty-two ❛r❜s, eighty-four ❛s❜s,",
  "seventy-six ❛t❜s, twenty-eight ❛u❜s, four ❛v❜s, four ❛W❜s,",
  "eighteen ❛w❜s, fourteen ❛x❜s, thirty-two ❛y❜s, four ❛:❜s,",
  "four ❛*❜s, twenty-six ❛-❜s, fifty-eight ❛,❜s,",
  "sixty ❛❛❜s and sixty ❛❜❜s, in a",
  "palindromic sequence",
  "whose second",
  "half runs",
  "thus:",
  ":suht",
  "snur flah",
  "dnoces esohw",
  "ecneuqes cimordnilap",
  "a ni ,s❜❜❛ ytxis dna s❜❛❛ ytxis",
  ",s❜,❛ thgie-ytfif ,s❜-❛ xis-ytnewt ,s❜*❛ ruof",
  ",s❜:❛ ruof ,s❜y❛ owt-ytriht ,s❜x❛ neetruof ,s❜w❛ neethgie",
  ",s❜W❛ ruof ,s❜v❛ ruof ,s❜u❛ thgie-ytnewt ,s❜t❛ xis-ytneves",
  ",s❜s❛ ruof-ythgie ,s❜r❛ owt-ytrof ,s❜q❛ ruof ,s❜p❛ ruof",
  ",s❜o❛ ruof-ytrof ,s❜n❛ owt-ytriht ,s❜m❛ ruof ,s❜l❛ xis",
  ",s❜i❛ thgie-ytrof ,s❜h❛ ytriht ,s❜g❛ neetxis",
  ",s❜f❛ thgie-ytriht ,s❜e❛ owt-ytfif",
  ",s❜d❛ net ,s❜c❛ thgie",
  ",s❜a❛ net nwod",
  "etirW",
  "*",
])

known_vector = {
  'a': 10,
  'c': 8,
  'd': 10,
  'e': 52,
  'f': 38,
  'g': 16,
  'h': 30,
  'i': 48,
  'l': 6,
  'm': 4,
  'n': 32,
  'o': 44,
  'p': 4,
  'q': 4,
  'r': 42,
  's': 84,
  't': 76,
  'u': 28,
  'v': 4,
  'W': 4,
  'w': 18,
  'x': 14,
  'y': 32,
  ':': 4,
  '*': 4,
  '-': 26,
  ',': 58,
  '❛': 60,
  '❜': 60,
}

single_digit = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
double_digit = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",]
below_hundred = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",]

hundred = "hundred"
thousand = "thousand"
million = "million"
billion = "billion"

def spell_number(n: int) -> str:
  if n <= 0: return ''
  if n < 10: return single_digit[n]
  if n < 20: return double_digit[n - 10]
  if n < 100:
    below, recurse = below_hundred[(n - (n % 10)) // 10 - 2], spell_number(n % 10)
    if len(recurse) == 0:
      return below
    return f"{below}-{recurse}"
  if n < 1_000: return f"{single_digit[n // 100]} {hundred} {spell_number(n % 100)}"
  if n < 1_000_000: return f"{spell_number(n // 1_000)} {thousand} {spell_number(n % 1_000)}"
  if n < 1_000_000_000: return f"{spell_number(n // 1_000_000)} {million} {spell_number(n % 1_000_000)}"
  return f"{spell_number(n // 1_000_000_000)} {billion} ${spell_number(n % 1_000_000_000)}"

def spell_char(c: str, n: int) -> str:
  return f"{spell_number(n).strip()} ❛{c}❜s"

def spell_chars(chars: Vector) -> str:
  spelled = [spell_char(c, n) for c, n in chars.items() if n > 0]
  [*parts, last] = spelled if len(spelled) > 0 else [""]
  return f"{", ".join(parts)} and {last}"

def spell_instructions(chars: Vector) -> str:
  return f"* Write down {spell_chars(chars)}, in a palindromic sequence whose second half runs thus:"
  return f"With that - please write down {spell_chars(chars)}, in a palindromic sequence whose second half runs thus:"

def spell_output(prefix: str, chars: Vector) -> str:
  start = f"{prefix} {spell_instructions(chars)}".strip()
  return f"{start}\n{start[::-1]}"

if spell_output('', known_vector) != known_text:
  expected = ''.join(known_text.split())
  computed = ''.join(spell_output('', known_vector).split())
  for i in range(0, min(len(expected), len(computed))):
    e, c = expected[i], computed[i]
    if e != c:
      print(f"Difference at position {i}: expected {e!r}, but got {c!r}.")
      print(f"Expected goes like this: {expected[i:]!r}")
      print(f"Computed goes like this: {computed[i:]!r}")
      break

changing_alphabet: Alphabet = sorted(list(set(
  "".join(single_digit + double_digit + below_hundred)
  + hundred
  + thousand
  + million
  + billion
  + spell_char('', 0)) - set(' ')))

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

def sum_vectors(*vectors: list[Vector]) -> Vector:
  result = {}
  for vector in vectors:
    for k, v in vector.items():
      result[k] = v + result.get(k, 0)
  return result

def scale_vector(vector: Vector, factor: int) -> Vector:
  return {k: v * factor for k, v in vector.items()}

def manhattan_distance(a: Vector, b: Vector) -> int:
  keys = set(a.keys()) + set(b.keys())
  return sum([abs(a[k] - b[k]) for k in keys])

def max_vectors(*vectors: list[Vector]) -> Vector:
  result = {}
  for vector in vectors:
    for k, v in vector.items():
      result[k] = max(v, result.get(k, 0))
  return result

def count_chars(s: str) -> Vector:
  counts = {}
  for c in "".join(s.split()):
    counts[c] = 1 + counts.get(c, 0)
  return counts

def get_base_vector(prefix: str) -> Vector:
  return count_chars(spell_output(prefix, []))

max_change_vector = scale_vector(max_vectors(*[count_chars(spell_number(n)) for n in range(100_000)]), 2)

delta_space: dict[str, list[int]] = {
    char: list(range(0, max_change_vector.get(char, 0) + 1, 2))
    for char in changing_alphabet}

def get_char_vectors(alphabet: Alphabet, base_vector: Vector, upper_limit: int) -> dict[str, list[(int, Vector)]]:
  char_vectors = {}

  for char in alphabet:
    lower_limit = base_vector.get(char, 0)
    char_vectors[char] = [
      # we scale by 2 because of the palindrome condition
      (count, scale_vector(count_chars(spell_char(char, count)), 2))
      # we step by 2 because of the palindrome condition
      for count in range(lower_limit, upper_limit, 2)]
    
  return char_vectors

# pulp is an mlp solver that could be useful
# highspy package for solver
