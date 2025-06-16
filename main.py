type Vector = dict[str, int]
type Alphabet = list[str]

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

def vector_sum(*vectors: list[Vector]) -> Vector:
  result = {}
  for vector in vectors:
    for k, v in vector.items():
      result[k] = v + result.get(k, 0)
  return result

def vector_scale(vector: Vector, factor: int) -> Vector:
  return {k: v * factor for k, v in vector.items()}

def vector_max(*vectors: list[Vector]) -> Vector:
  result = {}
  for vector in vectors:
    for k, v in vector.items():
      result[k] = max(v, result.get(k, 0))
  return result

def vector_eq(a:Vector, b:Vector) -> bool:
  keys = set(a.keys()) or set(b.keys())
  for k in keys:
    if a.get(k, 0) != b.get(k, 0):
      return False
  
  return True

def manhattan_distance(a: Vector, b: Vector) -> int:
  keys = set(a.keys()) + set(b.keys())
  return sum([abs(a[k] - b[k]) for k in keys])

def count_chars(s: str) -> Vector:
  counts = {}
  for c in "".join(s.split()):
    counts[c] = 1 + counts.get(c, 0)
  return counts

def get_base_vector(prefix: str) -> Vector:
  return count_chars(spell_output(prefix, []))

def get_char_vectors(alphabet: Alphabet, base_vector: Vector, upper_limit: int) -> dict[str, list[(int, Vector)]]:
  char_vectors = {}

  for char in alphabet:
    lower_limit = base_vector.get(char, 0)
    char_vectors[char] = [
      # we scale by 2 because of the palindrome condition
      (count, vector_scale(count_chars(spell_char(char, count)), 2))
      # we step by 2 because of the palindrome condition
      for count in range(lower_limit, upper_limit, 2)]
    
  return char_vectors

# pulp is an mlp solver that could be useful
# highspy package for solver

import pulp

if __name__ == '__main__':
  print(f"pulp got these solvers: {pulp.listSolvers(True)!r}")
