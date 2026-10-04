"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    all_listings = load_listings()
    results = []

    # clean search terms
    desc_words = [w.lower() for w in description.split() if len(w) > 1]
    target_size = size.strip().lower() if size else None

    for item in all_listings:
        # 1. price check
        if max_price is not None and item.get("price", 0) > max_price:
            continue

        # 2. size check
        if target_size:
            item_size = str(item.get("size", "")).strip().lower()
            # tokenize or split common separators like / or space
            tokens = [t.strip("()") for t in item_size.replace("/", " ").split()]
            if target_size not in tokens and target_size != item_size:
                continue

        # 3. keyword scoring across title, description, and style tags
        title = item.get("title", "").lower()
        desc = item.get("description", "").lower()
        tags = [str(t).lower() for t in item.get("style_tags", [])]
        combined = f"{title} {desc} {' '.join(tags)}"

        score = 0
        for w in desc_words:
            if w in combined:
                score += 1

        if score > 0:
            results.append((score, item))

    # sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    limit = getattr(config, "SEARCH_RESULT_LIMIT", 10)
    return [item for _, item in results[:limit]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
            specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    
    title = new_item.get("title", "thrift find")
    category = new_item.get("category", "")
    style = ", ".join(new_item.get("style_tags", []))
    desc = new_item.get("description", "")
    item_details = f"{title} (category: {category}, style tags: {style}). Description: {desc}"

    if not items:
        prompt = (
            f"Suggest 1-2 practical outfit ideas and styling advice for this thrift item:\n"
            f"{item_details}\n"
            f"The user has an empty wardrobe catalog, so recommend versatile general pieces to pair with it."
        )
    else:
        wardrobe_lines = []
        for itm in items:
            name = itm.get("name", "")
            cat = itm.get("category", "")
            tags = ", ".join(itm.get("style_tags", []))
            wardrobe_lines.append(f"- {name} [{cat}] ({tags})")
        wardrobe_text = "\n".join(wardrobe_lines)

        prompt = (
            f"Given this thrift item:\n{item_details}\n\n"
            f"And the user's current wardrobe:\n{wardrobe_text}\n\n"
            f"Suggest 1 or 2 specific outfit pairings combining the thrift item with pieces the user already owns."
        )

    system_prompt = "You are a thoughtful thrift stylist. Give clear, realistic outfit recommendations."
    return generate(prompt, system=system_prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    title = new_item.get("title", "thrift find")
    price = new_item.get("price", 0.0)
    platform = new_item.get("platform", "online")

    if not outfit or not outfit.strip():
        return f"Found this {title} for ${price:.2f} on {platform}! Great vintage find waiting for the right fit."

    prompt = (
        f"Write a short, engaging social post caption (2 to 4 sentences) showing off this thrift find.\n"
        f"Item: {title}\n"
        f"Price: ${price:.2f}\n"
        f"Platform: {platform}\n"
        f"Outfit ideas: {outfit}\n\n"
        f"Requirements:\n"
        f"- Read like a real person posting their thrift haul, not an ad or catalog description.\n"
        f"- Explicitly mention the item title, the exact price (${price:.2f}), and the platform ({platform}) once each.\n"
        f"- Keep it between 2 and 4 sentences."
    )

    system_prompt = "You are a thrifter writing an authentic, punchy caption about a vintage clothing find."
    return generate(prompt, system=system_prompt)
