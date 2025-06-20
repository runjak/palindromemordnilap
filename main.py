import pulp

type Vector = dict[str, int]
type Alphabet = list[str]

single_digit = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
double_digit = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",]
below_hundred = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",]

hundred = "hundred"
thousand = "thousand"
million = "million"
billion = "billion"
dash = '-'

def spell_number(n: int) -> str:
  if n <= 0: return ''
  if n < 10: return single_digit[n]
  if n < 20: return double_digit[n - 10]
  if n < 100:
    below, recurse = below_hundred[(n - (n % 10)) // 10 - 2], spell_number(n % 10)
    if len(recurse) == 0:
      return below
    return f"{below}{dash}{recurse}"
  if n < 1_000: return f"{single_digit[n // 100]} {hundred} {spell_number(n % 100)}"
  if n < 1_000_000: return f"{spell_number(n // 1_000)} {thousand} {spell_number(n % 1_000)}"
  if n < 1_000_000_000: return f"{spell_number(n // 1_000_000)} {million} {spell_number(n % 1_000_000)}"
  return f"{spell_number(n // 1_000_000_000)} {billion} ${spell_number(n % 1_000_000_000)}"

def spell_char(c: str, n: int) -> str:
  if n == 0:
    return ''
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
  letters += dash + hundred  + thousand + million + billion
  letters += spell_char('a', 1) + spell_chars({}) + spell_instructions({}, prefix, suffix)
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

def get_alphabet_choices(alphabet: Alphabet, lower_bounds: Vector, upper_bound: int) -> dict[str, list[(int, pulp.LpVariable, Vector)]]:
  alphabet_vectors = {}

  for char in alphabet:
    lower_bound = lower_bounds.get(char, 0)
    alphabet_vectors[char] = [
      (count, pulp.LpVariable(name=f"{char}_{count}", lowBound=0, upBound=1, cat=pulp.LpBinary),
        # we scale by 2 because of the palindrome condition
        vector_scale(count_chars(spell_char(char, count)), 2))
      # we step by 2 because of the palindrome condition
      for count in range(lower_bound, lower_bound + upper_bound, 2)]
    
  return alphabet_vectors

def alphabet_choices_by_variable(alphabet_choices: dict[str, list[(int, pulp.LpVariable, Vector)]]) -> dict[pulp.LpVariable, (str, int)]:
  return {
    variable: (letter, count)
    for letter, choices in alphabet_choices.items()
    for (count, variable, _) in choices}

def compute_contributors(alphabet_choices: dict[str, list[(int, pulp.LpVariable, Vector)]]) -> dict[str, list[(int, pulp.LpVariable)]]:
  """
  For every letter we compute:
  - A list[(int, pulp.LpVariable)] of weights and variables that contribute to this letter.
  """
  contributors = {letter: [] for letter in alphabet_choices.keys()}

  for letter_choices in alphabet_choices.values():
    for (_, variable, vector) in letter_choices:
      for letter, weight in vector.items():
        contributors[letter] = contributors.get(letter, []) + [(weight, variable)]
        # contributors[letter].append((weight, variable))
  
  return contributors

def implies(a: pulp.LpVariable, b: pulp.LpVariable) -> pulp.LpConstraint:
  """
    How do implications work in ILP?
    a -> b

    !a | b
    1 1 1
    1 0 0
    0 1 1
    0 0 1

    a - b < 1
    1 1 ( 0) 1
    1 0 ( 1) 0
    0 1 (-1) 1
    0 0 ( 0) 1

    a - b <= 0
  """
  return a - b <= 0

def absolute(x: pulp.LpVariable):
  """
  How do you constrain the absolute value of some variable?

  Structure that is {1, -1}: (1 - 2b)
  """
  None

def letter_constraints(alphabet_choices: dict[str, list[(int, pulp.LpVariable, Vector)]], lower_bounds: Vector) -> list[pulp.LpConstraint]:
  contributors = compute_contributors(alphabet_choices=alphabet_choices)
  constraints = []

  for letter, letter_choices in alphabet_choices.items():
    contributor_sum = lower_bounds.get(letter, 0) + sum([weight * contributor_variable for (weight, contributor_variable) in contributors[letter]])
    for (count, letter_variable, _) in letter_choices:
      weighted_letter = count * letter_variable
      constraints += [implies(weighted_letter, contributor_sum)]
      # I'm not sure what to make of this. There's some kind of issue here and I don't know why/which.
      # constraints += [implies(weighted_letter, contributor_sum), implies(contributor_sum, weighted_letter)]

  return constraints

def print_problem(problem: pulp.LpProblem, alphabet_choices: dict[str, list[(int, pulp.LpVariable, Vector)]]) -> None:
  by_variable = alphabet_choices_by_variable(alphabet_choices=alphabet_choices)
  vector = {}
  
  print(f"Problem status: {pulp.LpStatus[problem.status]}")
  for v in problem.variables():
    value = int(v.varValue)
    if value != 0:
      print(f"{v.name}={v.varValue}")
      (letter, count) = by_variable[v]
      vector[letter] = count
  
  print(spell_instructions(vector, default_prefix, default_suffix))

def main():
  prefix = default_prefix
  suffix = default_suffix
  lower_bounds = get_lower_bounds(prefix)
  upper_bound = 100
  alphabet = get_alphabet(prefix, suffix)

  print(f"Alphabet: {alphabet}")
  print(f"Lower bounds: {lower_bounds}")

  problem = pulp.LpProblem(name="Fiddling", sense=pulp.LpMinimize)

  alphabet_choices = get_alphabet_choices(
    alphabet=alphabet,
    lower_bounds=lower_bounds,
    upper_bound=upper_bound)

  """
  What do we even optimize here?
  We want to minimize a distance.
  The distance is between:
  - The sum of all picked per-letter weights
  - The sum of all picked contributing weights plus the base vector
  """
  sum_of_per_letter_weights = sum([
    weight * letter_variable
    for letter_choices in alphabet_choices.values()
    for (weight, letter_variable, _) in letter_choices
    ])
  
  # FIXME is this right to just sum up, or should it be the sum of per-letter distances instead?
  # It is not right, but maybe still interesting o.O

  contributors = compute_contributors(alphabet_choices=alphabet_choices)
  sum_of_all_contributing_weights_plus_base = None
  for letter, letter_contributors in contributors.items():
    base = lower_bounds.get(letter, 0)
    None

  # For every letter we choose at exactly one variable
  for choices in alphabet_choices.values():
    problem += sum([variable for (_, variable, _) in choices]) == 1
  
  for constraint in letter_constraints(alphabet_choices=alphabet_choices, lower_bounds=lower_bounds):
    problem += constraint

  problem.solve(solver=pulp.HiGHS())
  print_problem(problem, alphabet_choices=alphabet_choices)


def experiment_e():
  print("Experiment e\n")
  
  prefix = "The number of e's in this text is: "
  lower_limit = count_chars(prefix).get('e', 0)
  upper_limit = lower_limit + 4

  print(f"Choosing 'e' count from [{lower_limit}, {upper_limit}] for 'e's in\n\t{prefix!r}")

  e_variables = {
    pulp.LpVariable(name=f"e_{count}", cat=pulp.LpBinary): count
    for count in range(lower_limit, upper_limit + 1)}
  
  e_offsets = {count: count_chars(spell_number(count)).get('e', 0) for count in e_variables.values()}
  print(f"e_offsets:{e_offsets!r}")
  total_number_of_e_s = lower_limit + sum([c * v for v, c in e_variables.items()])

  problem = pulp.LpProblem(name="Experiment_e", sense=pulp.LpMinimize)

  # Make sure we choose only one count:
  problem += sum(e_variables.keys()) == 1, "pick exactly one 'e'"

  # Construct e count constraint
  offset_sum = sum([e_offsets.get(c, 0) * v for v, c in e_variables.items()])
  weighted_variables = sum([-c * v for v, c in e_variables.items()])
  problem += lower_limit + offset_sum + weighted_variables == 0

  problem.solve(solver=pulp.HiGHS())
  print(f"Problem status: {pulp.LpStatus[problem.status]}")
  for v in problem.variables():
    value = int(v.varValue)
    if value != 0:
      print(f"{v.name}={v.varValue}")
      print(f"{prefix + spell_number(e_variables[v])!r}")

def new_main():
  print("new_main()\n")
  prefix = default_prefix
  suffix = default_suffix

  alphabet = get_alphabet(prefix=prefix, suffix=suffix)
  bound_delta = 100

  lower_bounds = {letter: 0 for letter in alphabet} | get_lower_bounds(prefix)
  upper_bounds = {letter: count + bound_delta for letter, count in lower_bounds.items()}

  letter_variables_counts = {letter: {pulp.LpVariable(name=f"{letter}_{count}", cat=pulp.LpBinary): count for count in range(lower_bounds[letter], upper_bounds[letter] + 1, 2)} for letter in alphabet}
  
  """
  We map each letter to a list of tuples.
  These tuples are weight, variable for every variable
  that contributes to the offset count of a letter.
  """
  letter_count_offsets: dict[str, list[(int, pulp.LpVariable)]] = {letter: [] for letter in alphabet}

  for letter, choices in letter_variables_counts.items():
    for variable, count in choices.items(): # e_68, 68
      offset_vector = vector_scale(count_chars(spell_char(letter, count)), 2) # 2 * (achtundsechtzig es -> a:1, c:2)
      for offset_letter, offset_count in offset_vector.items():
        letter_count_offsets[offset_letter].append((offset_count, variable))

  problem = pulp.LpProblem(name="Experiment_e", sense=pulp.LpMinimize)

  # For every letter we chose exactly one count:
  for letter, choices in letter_variables_counts.items():
    problem += sum(choices.keys()) == 1, f"pick exactly one {letter!r}"
  
  # For every letter we have a letter specific constraint
  for letter in alphabet:
    # FIXME for ',' we need something extra
    offset_sum = sum([c * v for c, v in letter_count_offsets[letter]])
    weighted_variables = sum([-c * v for v, c in letter_variables_counts[letter].items()])
    problem += lower_bounds[letter] + offset_sum + weighted_variables == 0

  print(letter_count_offsets['e'])

  problem.solve(solver=pulp.HiGHS())

  print(f"Problem status: {pulp.LpStatus[problem.status]}")
  for v in problem.variables():
    value = int(v.varValue)
    if value != 0:
      print(f"{v.name}={value} ({v.varValue})")

if __name__ == '__main__':
  print(f"pulp got these solvers: {pulp.listSolvers(True)!r}")
  # experiment_e()
  new_main()
  # main()
