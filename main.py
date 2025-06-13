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
  if n < 100: return f"{below_hundred[(n - (n % 10)) // 10 - 2]} {spell_number(n % 10)}"
  if n < 1_000: return f"{single_digit[n // 100]} {hundred} {spell_number(n % 100)}"
  if n < 1_000_000: return f"{spell_number(n // 1_000)} {thousand} {spell_number(n % 1_000)}"
  if n < 1_000_000_000: return f"{spell_number(n // 1_000_000)} {million} {spell_number(n % 1_000_000)}"
  return f"{spell_number(n // 1_000_000_000)} {billion} ${spell_number(n % 1_000_000_000)}"

def spell_char(c: str, n: int) -> str:
  return f"{spell_number(n)} ❛{c}❜s"

type CharCounts = list[(str, int)]

def spell_chars(chars: CharCounts) -> str:
  spelled = [spell_char(c, n) if n > 0 else "" for (c, n) in chars]
  [*parts, last] = spelled if len(spelled) > 0 else [""]
  return f"{", ".join(parts)} and {last}"

def spell_instructions(chars: CharCounts) -> str:
  return f"Write down {spell_chars(chars)}, in a palindromic sequence whose second half runs thus:"
  return f"With that - please write down {spell_chars(chars)}, in a palindromic sequence whose second half runs thus:"

def spell_output_counts(prefix: str, chars: CharCounts) -> str:
  start = f"{prefix} {spell_instructions(chars)}"
  return f"{start}\n{start[::-1]}"

type Alphabet = list[str]

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

type Vector = dict[str, int]

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

def vector_to_char_counts(vector: Vector) -> CharCounts:
  return [(k, vector[k]) for k in sorted(vector.keys())]

def max_vectors(*vectors: list[Vector]) -> Vector:
  result = {}
  for vector in vectors:
    for k, v in vector.items():
      result[k] = max(v, result.get(k, 0))
  return result

def spell_output_vector(prefix: str, vector: Vector) -> str:
  return spell_output_counts(prefix, vector_to_char_counts(vector))

def count_chars(s: str) -> Vector:
  counts = {}
  for c in "".join(s.split()):
    counts[c] = 1 + counts.get(c, 0)
  return counts

def get_base_vector(prefix: str) -> Vector:
  return count_chars(spell_output_counts(prefix, []))

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

def experiment_fixpoint(prefix: str) -> Vector:
  alphabet = get_alphabet(prefix)
  base_vector = get_base_vector(prefix)

  char_counts = {char: base_vector.get(char, 0) for char in alphabet}
  char_vectors = {char: scale_vector(count_chars(spell_char(char, char_counts[char])), 2) for char in alphabet}
  
  char_sums = sum_vectors(base_vector, *char_vectors.values())
  
  while True:
    for char, char_sum in char_sums.items():
      char_count = char_counts[char]
      
      if char_sum == char_count:
        continue

      char_vector = scale_vector(count_chars(spell_char(char, char_sum)), 2)
      char_sums = sum_vectors(char_sums, scale_vector(char_vectors[char], -1), char_vector)
      char_counts[char] = char_sum
      char_vectors[char] = char_vector
      break
    else: break
  
  return char_sums

import random

def experiment_weights(prefix: str, upper_limit: int, sample_count: int, generation_count: int) -> Vector:
  alphabet = get_alphabet(prefix)
  base_vector = get_base_vector(prefix)
  char_vectors = get_char_vectors(alphabet, base_vector, upper_limit)

  def normalize_weights(ps: list[float]) -> list[float]:
    s = sum(list)
    return [p/s for p in ps]
  
  char_weights = {char: normalize_weights([1] * len(vectors)) for char, vectors in char_vectors.items()}

  def choose_char_vectors() -> list[(str, int, Vector)]:
    char_vectors = []
    for char, population in char_vectors.items():
      [(count, vector)] = random.choices(population, char_weights, k=1)
      char_vectors.append((char, count, vector))
    return char_vectors
  
  def choice_error(choice: list[(str, int, Vector)]) -> int:
    a = sum_vectors(base_vector, *[vector for (_, _, vector) in choice])
    b = sum_vectors(base_vector, {char: count for (char, count, _) in choice})
    return manhattan_distance(a, b)
  
  def sample_errors() -> Vector:
    errors = {}
    
    for _ in range(sample_count):
      choice = choose_char_vectors()
      error = choice_error(choice)
      for (char, _, _) in choice:
          errors[char] = error + errors.get(char, 0)

    return errors
  
  def generate():
    for _ in range(generation_count):
      errors = sample_errors()
      None # FIXME do something to the weights here.

  # FIXME we will continue down here.
