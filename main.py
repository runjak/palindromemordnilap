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

def spell_instructions(chars: Vector, prefix: str, suffix: str) -> str:
  return f"{prefix}{spell_chars(chars)}{suffix}".strip()

default_prefix = '* Write down '
default_suffix = ', in a palindromic sequence whose second half runs thus:'

def spell_output(chars: Vector, prefix=default_prefix, suffix=default_suffix) -> str:
  start = f"{spell_instructions(chars, prefix, suffix)}".strip()
  return f"{start}\n{start[::-1]}"

def get_alphabet(prefix: str, suffix: str) -> Alphabet:
  letters = "".join(single_digit + double_digit + below_hundred) 
  letters += hundred  + thousand + million + billion
  letters += spell_char('', 0) + spell_chars({}) + spell_instructions({}, prefix, suffix)
  letters += prefix
  letters = "".join(letters.split())
  return sorted(list(set(letters)))

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

def get_lower_bounds(prefix: str) -> Vector:
  return vector_scale(count_chars(spell_output({}, prefix)), 2)

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

import pulp

def print_problem(problem: pulp.LpProblem):
  print(f"Problem status: {pulp.LpStatus[problem.status]}")
  for v in problem.variables():
    print(f"{v.name}={v.varValue}")

def example_problem() -> pulp.LpProblem:
  v1 = pulp.LpVariable("v1", lowBound=5, upBound=11, cat=pulp.LpInteger)
  v2 = pulp.LpVariable("v2", lowBound=2, upBound=13, cat=pulp.LpInteger)

  problem = pulp.LpProblem("Example_problem", pulp.LpMaximize)
  # Objective function added first
  problem += 2 * v1 + 3 * v2
  # Additional constraint
  problem += v1 + v2 <= 11
  
  return problem

if __name__ == '__main__':
  print(f"pulp got these solvers: {pulp.listSolvers(True)!r}")

  prefix = default_prefix
  suffix = default_suffix
  lower_bounds = get_lower_bounds(prefix)
  alphabet = get_alphabet(prefix, suffix)
  char_vectors = get_char_vectors(alphabet=alphabet, base_vector=lower_bounds, upper_limit=100)

  print(f"Alphabet: {alphabet}")
  print(f"Lower bounds: {lower_bounds}")
  print(f"char vectors: {char_vectors}")

  problem = example_problem()
  problem.solve(solver=pulp.HiGHS())
  print_problem(problem)

