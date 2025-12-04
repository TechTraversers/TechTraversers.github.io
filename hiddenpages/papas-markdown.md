
`=LOOKUP(2,1/(A2:A100<>""),A2:A100)`

```excel
=LOOKUP(2,1/(A2:A100<>""),A2:A100)
```

Here’s a clear, older-Excel-friendly breakdown of how the formula works behind the scenes. The goal: make the LOOKUP trick feel logical instead of magical.

---

## The formula

```excel
=LOOKUP(2,1/(A2:A100<>""),A2:A100)
```

This returns the last non-empty value in the range A2:A100.

---

## Step-by-step explanation

We’ll walk through the three parts.

### 1) (A2:A100 <> "")

This checks each cell and produces an array of TRUE/FALSE values.

Example (imagine A2–A8):

```text
A2: Apple      → TRUE
A3: (blank)    → FALSE
A4: Cat        → TRUE
A5: Dog        → TRUE
A6: (blank)    → FALSE
A7: Pizza      → TRUE
A8: (blank)    → FALSE
```

So the array looks like:

```text
{TRUE, FALSE, TRUE, TRUE, FALSE, TRUE, FALSE}
```

### 2) 1 / (A2:A100<>"")

Divide 1 by each TRUE/FALSE.

* TRUE behaves like 1 → `1/1 = 1`
* FALSE behaves like 0 → `1/0 = #DIV/0!` (an error)

The array becomes:

```text
{1, #DIV/0!, 1, 1, #DIV/0!, 1, #DIV/0!}
```

Non-empty cells are represented by `1`; empty cells become a division error.

### 3) LOOKUP(2, lookup_array, result_array)

Now the trick:

* LOOKUP searches for the largest value less than or equal to the lookup value (2).
* Errors are ignored by LOOKUP.
* All non-empty cells provide `1` in the lookup array. Since `1 ≤ 2`, LOOKUP finds the last `1` and returns the corresponding value from the result array (`A2:A100`).

So the formula returns the last filled cell in the range.

---

## Why this works (and why it's useful)

* LOOKUP ignores errors and does an approximate match.
* Choosing `2` ensures no exact match is found, so LOOKUP falls back to the last valid `1` in the lookup array.
* Works in older Excel versions (no dynamic arrays, no Ctrl+Shift+Enter needed).
* Works with text and numbers and is efficient on large ranges.

---

## Example walkthrough

If A2:A8 contains:

```text
Apple
(blank)
Cat
Dog
(blank)
Pizza
(blank)
```

Then the intermediate steps are:

1) TRUE/FALSE → `{T, F, T, T, F, T, F}`
2) 1/(...) → `{1, err, 1, 1, err, 1, err}`
3) LOOKUP(2,...) finds the last `1` (Pizza) and returns `Pizza`.

---

## Notes

* Works reliably in legacy Excel versions because LOOKUP's approximate-match behavior is longstanding.
* Use a slightly larger lookup value (like `2`) than the values produced in the lookup array (`1`) to force the last match behavior.
* This trick is handy when you need the last non-empty cell without VBA or modern dynamic array functions.
