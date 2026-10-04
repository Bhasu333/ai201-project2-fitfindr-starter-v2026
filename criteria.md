# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Keyword search can occasionally mismatch or model calls might hiccup, but with clear queries it should complete reliably. 4 of 5 gives room for one flaky model generation or edge case while still demanding high reliability on the happy path.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This is pure deterministic code in the planning loop. When `search_listings` returns an empty list, the branch condition should trigger every single time without exception.

---

## 3. Selected item in session matches item passed to suggest_outfit

Across 5 separate runs of matching queries, the `id` of `session["selected_item"]` exactly equals the `id` of the item passed into `suggest_outfit` and `create_fit_card` — 5 of 5 tries.

**Why this target:**
State passing through the session dictionary is deterministic application logic. If state drops or gets replaced by another item between tool calls, that's a code bug in our state flow, so it should pass 5 of 5 times.

---

## 4. Fit card mentions the price of the selected item

For matching queries that return a fit card, the text in `session["fit_card"]` includes the exact price or dollar amount of `session["selected_item"]` (e.g. "$18" or "$18.00") — in at least 4 of 5 tries.

**Why this target:**
Fit cards are meant to be social posts sharing a thrift find, so price is a core detail. Because LLM outputs vary by temperature, the model might occasionally rephrase or omit the dollar sign, so 4 of 5 accounts for slight prompt adherence variance.

---

## 5. Empty wardrobe returns styling advice without crashing

Given a matching query and an empty wardrobe (`wardrobe["items"] == []`), the agent completes all three tools and returns a non-empty `session["fit_card"]` — in at least 4 of 5 tries.

**Why this target:**
New users starting out with an empty wardrobe shouldn't crash the agent. The tool should handle the empty items list by providing general styling ideas, with 4 of 5 accounting for any generation hiccups.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
