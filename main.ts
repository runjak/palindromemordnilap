/**
 * https://runjak.codes/palindromemordnilap/
 * https://www.w3resource.com/javascript-exercises/javascript-math-exercise-105.php
 */

const single_digit = [
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
];
const double_digit = [
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
];
const below_hundred = [
  "twenty",
  "thirty",
  "forty",
  "fifty",
  "sixty",
  "seventy",
  "eighty",
  "ninety",
];

/**
 * Taken from https://www.w3resource.com/javascript-exercises/javascript-math-exercise-105.php
 */
const spellNumber = (n: number) => {
  if (n < 0 || Number.isNaN(n)) {
    throw new Error(`Invalid value of n: ${n}`);
  }

  if (n === 0) {
    return "";
  }

  if (n < 10) {
    return single_digit[n];
  } else if (n < 20) {
    return double_digit[n - 10];
  } else if (n < 100) {
    return `${below_hundred[(n - (n % 10)) / 10 - 2]} ${spellNumber(n % 10)}`;
  } else if (n < 1000) {
    return `${single_digit[Math.trunc(n / 100)]} hundred ${spellNumber(
      n % 100
    )}`;
  } else if (n < 1000000) {
    return `${spellNumber(Math.floor(n / 1000))} thousand ${spellNumber(
      n % 1000
    )}`;
  } else if (n < 1000000000) {
    return `${spellNumber(Math.floor(n / 1000000))} million ${spellNumber(
      n % 1000000
    )}`;
  } else {
    return `${spellNumber(Math.floor(n / 1000000000))} billion ${spellNumber(
      n % 1000000000
    )}`;
  }
};

type CharCounts = Map<string, number>;

const countChars = (message: string): CharCounts => {
  const chars = Array.from(message.replace(/\W/g, "")); // FIXME filter whitespace
  let counts = new Map<string, number>();

  for (let char of chars) {
    char = char.toLowerCase();
    counts.set(char, 1 + (counts.get(char) ?? 0));
  }

  return counts;
};

const spellChars = (counts: CharCounts): string => {
  const parts = Array.from(counts.keys())
    .sort()
    .map((key) => `${spellNumber(counts.get(key) ?? 0)} ❛${key}❜s`);

  return `${parts.slice(0, parts.length - 1).join(", ")} and ${
    parts[parts.length - 1]
  }`;
};

const spellInstructions = (counts: CharCounts): string =>
  `With that - please write down ${spellChars(
    counts
  )}, in a palindromic sequence whose second half runs thus:`;

const equalCounts = (count1: CharCounts, count2: CharCounts): boolean => {
  if (count1.size !== count2.size) {
    return false;
  }

  for (let key of count1.keys()) {
    if (count1.get(key) !== count2.get(key)) {
      return false;
    }
  }

  return true;
};

const reverse = (message: string): string =>
  message.split("").reverse().join("");

const toPalindrome = (message: string): string =>
  `${message}\n${reverse(message)}`;

const fixpoint = (prefix: string): [string, boolean] => {
  let message = toPalindrome(
    `${prefix} ${spellInstructions(countChars(prefix))}`
  );
  let valid = false;

  // 1_000_000 runs about a minute
  const minute = 1_000_000;
  for (let i = 0; i < 30 * minute; i++) {
    const nextCount = countChars(message);
    const nextMessage = toPalindrome(
      `${prefix} ${spellInstructions(nextCount)}`
    );

    if (nextMessage === message) {
      valid = true;
      break;
    }

    message = nextMessage;
  }

  return [message, valid];
};

console.log(
  fixpoint(
    "Dear Gridfuse, I enjoyed our time together. I hope you'll do well. Love ya."
  )
);
