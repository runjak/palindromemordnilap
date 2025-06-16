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

import main

if main.spell_output('', known_vector) != known_text:
  expected = ''.join(known_text.split())
  computed = ''.join(main.spell_output('', known_vector).split())
  for i in range(0, min(len(expected), len(computed))):
    e, c = expected[i], computed[i]
    if e != c:
      print(f"Difference at position {i}: expected {e!r}, but got {c!r}.")
      print(f"Expected goes like this: {expected[i:]!r}")
      print(f"Computed goes like this: {computed[i:]!r}")
      break

assert main.vector_eq(known_vector, main.count_chars(known_text)), "Somethings wrong with the count"
