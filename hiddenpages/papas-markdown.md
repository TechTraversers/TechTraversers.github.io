
`=LOOKUP(2,1/(A2:A100<>""),A2:A100)`




Here’s a **clear, older-Excel-friendly** breakdown of how the formula works behind the scenes. This will make the whole “LOOKUP trick” feel logical instead of magical.

---

# ✔ The formula

```excel
=LOOKUP(2,1/(A2:A100<>""),A2:A100)
```

This returns the **last non-empty value** in A2:A100.

---

# ✔ Step-by-step explanation

We’ll walk through the three parts:

## **1. (A2:A100 <> "")**

This checks each cell and produces an **array of TRUE/FALSE** values.

Example (imagine A2–A8):

```
A2: Apple      → TRUE
A3: (blank)    → FALSE
A4: Cat        → TRUE
A5: Dog        → TRUE
A6: (blank)    → FALSE
A7: Pizza      → TRUE
A8: (blank)    → FALSE
```

So the array looks like:

```
{TRUE, FALSE, TRUE, TRUE, FALSE, TRUE, FALSE}
```

---

## **2. 1 / (A2:A100<>"")**

Now we divide 1 by each TRUE or FALSE.

* TRUE acts like **1** → `1/1 = 1`
* FALSE acts like **0** → `1/0 = #DIV/0!` (an error)

So the array becomes:

```
{1, #DIV/0!, 1, 1, #DIV/0!, 1, #DIV/0!}
```

Only non-empty cells become a **1**.
Empty cells become an **error**.

---

## **3. LOOKUP(2, these_values, A2:A100)**

Now the clever trick.

### How LOOKUP behaves:

* LOOKUP searches for the largest value **≤ 2**.
* Errors (`#DIV/0!`) are ignored.
* All the non-empty cells appear as **1** in the lookup array.
* 1 is ≤ 2, so LOOKUP will use **the last 1 in the array**.

Since the 1’s correspond to non-empty entries, the **last 1** corresponds to the **last filled cell** in A2:A100.

LOOKUP then returns the value from the result array (**A2:A100**) at that same position.

---

# ✔ Why it’s brilliant

Because LOOKUP:

* **Ignores errors**
* **Searches from top to bottom**
* **Returns the last matching item when the lookup value is “too big”**

Choosing **2** as the lookup value guarantees there is no exact match, so it returns the **last possible good value**.

---

# ✔ Example walkthrough

Imagine A2:A8 contains:

```
Apple
(blank)
Cat
Dog
(blank)
Pizza
(blank)
```

Step 1: TRUE/FALSE

```
{T, F, T, T, F, T, F}
```

Step 2: 1/(…)

```
{1, err, 1, 1, err, 1, err}
```

Step 3: LOOKUP(2,…)

* LOOKUP scans for the last **1**.
* The last 1 is at the row containing **Pizza**.
* So it returns **Pizza**.

---

# ✔ Why this works in old Excel

* No dynamic arrays needed
* No Ctrl+Shift+Enter
* LOOKUP’s "approximate match" behavior goes back decades
* Works with text and numbers
* Fast even on large spreadsheets
