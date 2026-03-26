print("Elias scorer starting...")

import openai
from supabase import create_client
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

print("All connected.")

SUBREDDIT_MAP = {
    "WaltDisneyWorld":      "WDW",
    "DisneyWorld":          "WDW",
    "WDW":                  "WDW",
    "GalacticStarcruiser":  "WDW",
    "MagicKingdom":         "WDW",
    "EPCOT":                "WDW",
    "HollywoodStudios":     "WDW",
    "AnimalKingdom":        "WDW",
    "DisneySprings":        "WDW",
    "WDWPlanning":          "WDW",
    "Disneyland":           "DL",
    "CaliforniaAdventure":  "DL",
    "DisneylandResort":     "DL",
    "DCA":                  "DL",
    "DisneyCruiseLife":     "Cruises",
    "DCL":                  "Cruises",
    "DisneyCruise":         "Cruises",
    "DisneyResorts":        "Hotels",
    "DisneyVacationClub":   "Hotels",
    "DVC":                  "Hotels",
    "disneyparks":          None,
    "disney":               None,
    "DisneyPlanning":       None,
    "StarWars":             None,
    "saltierthancrait":     None,
    "videos":               None,
    "blankies":             None,
    "news":                 None,
    "television":           None,
    "entertainment":        None,
}

PROJECT_KEYWORDS = {
    "Galactic Starcruiser": [
        "starcruiser", "star cruiser", "galactic starcruiser",
        "halcyon", "star wars hotel", "starcruiser hotel",
        "$6000", "$5000", "two night", "2 night stay",
        "immersive hotel", "larp hotel"
    ],
    "Galaxy's Edge": [
        "galaxy's edge", "galaxys edge", "batuu",
        "rise of the resistance", "rise of resistance",
        "smuggler's run", "smugglers run", "millennium falcon",
        "black spire", "star wars land"
    ],
    "Tron Lightcycle Run": [
        "tron", "lightcycle", "tron ride", "tron coaster"
    ],
    "Guardians Coaster": [
        "guardians", "guardians of the galaxy", "cosmic rewind",
        "epcot coaster", "guardians coaster"
    ],
    "Remy's Ratatouille": [
        "remy", "ratatouille", "rat ride", "france pavilion ride"
    ],
    "Haunted Mansion": [
        "haunted mansion", "doom buggy", "ghost host",
        "stretching room", "999 happy haunts"
    ],
    "Space Mountain": [
        "space mountain", "space mtn"
    ],
    "EPCOT": [
        "epcot", "world showcase", "future world",
        "international festival", "flower and garden",
        "food and wine", "festival of the arts"
    ],
    "Magic Kingdom": [
        "magic kingdom", "mk ", " mk,", "main street usa",
        "cinderella castle", "cinderella's castle",
        "fantasyland", "tomorrowland", "adventureland",
        "frontierland", "liberty square"
    ],
    "Hollywood Studios": [
        "hollywood studios", "dhs", "tower of terror",
        "slinky dog", "toy story land", "indiana jones stunt",
        "muppet vision"
    ],
    "Animal Kingdom": [
        "animal kingdom", "ak ", " ak,", "avatar",
        "pandora", "flight of passage", "na'vi river",
        "expedition everest", "kilimanjaro safari"
    ],
    "Genie+": [
        "genie+", "genie plus", "lightning lane",
        "individual lightning lane", "fastpass",
        "fast pass", "virtual queue", "boarding group"
    ],
    "My Disney Experience": [
        "my disney experience", "mde", "disney app",
        "mobile order", "mobile ordering", "park pass",
        "park reservation"
    ],
    "Disneyland Park": [
        "disneyland park", "anaheim", "matterhorn",
        "new orleans square", "critter country",
        "indiana jones adventure"
    ],
    "California Adventure": [
        "california adventure", "dca", "carsland",
        "cars land", "radiator springs", "web slingers",
        "avengers campus", "soarin", "incredicoaster",
        "buena vista street"
    ],
    "Disney Cruise Line": [
        "disney cruise", "dcl", "disney wish", "disney fantasy",
        "disney dream", "disney magic", "disney wonder",
        "castaway cay", "disney treasure", "cruise ship",
        "stateroom", "rotational dining"
    ],
    "Grand Floridian": [
        "grand floridian", "grand flo", "gf resort"
    ],
    "Polynesian Resort": [
        "polynesian", "poly resort", "disney polynesian"
    ],
    "Wilderness Lodge": [
        "wilderness lodge", "fort wilderness"
    ],
    "Disney Hotels": [
        "disney resort hotel", "disney hotel", "disney resort",
        "value resort", "moderate resort", "deluxe resort",
        "vacation club", "dvc resort"
    ],
}

def assign_project_tags(content, post_title):
    text = (content + " " + post_title).lower()
    tags = []
    for project, keywords in PROJECT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(project)
    return tags if tags else ["General Disney"]

def infer_experience(subreddit, content, post_title):
    mapped = SUBREDDIT_MAP.get(subreddit)
    if mapped is not None:
        return mapped
    text = (content + " " + post_title).lower()
    if any(w in text for w in ["disneyland", "california adventure", "anaheim", "dca"]):
        return "DL"
    if any(w in text for w in ["cruise", "dcl", "disney wish", "castaway"]):
        return "Cruises"
    if any(w in text for w in ["grand floridian", "polynesian", "wilderness lodge",
                                "boardwalk inn", "yacht club", "beach club",
                                "art of animation", "pop century", "all star"]):
        return "Hotels"
    if any(w in text for w in ["disney world", "wdw", "orlando", "magic kingdom",
                                "epcot", "animal kingdom", "hollywood studios",
                                "starcruiser", "halcyon", "galaxy's edge",
                                "batuu", "tron", "guardians"]):
        return "WDW"
    return "WDW"


# ── Rubric gates (Pass 1 outputs rubric_total 0-10) ──────────────────────────
RUBRIC_REJECT_BELOW = 4.0
RUBRIC_ACCEPT_NO_PASS2 = 7.0
RUBRIC_STRONG_OVERRIDE = 8.0

def _safe_float(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def rubric_pass_decision(score: dict) -> tuple[str, str | None]:
    """Return ('reject', reason), ('accept', None), or ('borderline', None)."""
    r = _safe_float(score.get("rubric_total"), 0.0)
    ins = bool(score.get("is_insightful"))
    if r < RUBRIC_REJECT_BELOW:
        return "reject", "rubric_below_4"
    if r >= RUBRIC_STRONG_OVERRIDE:
        return "accept", None
    if r >= RUBRIC_ACCEPT_NO_PASS2:
        return "accept", None
    if not ins:
        return "reject", "pass1_not_insightful"
    if RUBRIC_REJECT_BELOW <= r < RUBRIC_ACCEPT_NO_PASS2:
        return "borderline", None
    return "reject", "rubric_weak"


# ── PASS 1: Initial scoring ───────────────────────────────────────────────────
def score_batch(comments, high_tier=False):
    comment_list = ""
    for i, c in enumerate(comments):
        comment_list += (
            f"\nComment {i+1} "
            f"[Subreddit: r/{c.get('subreddit','unknown')} | "
            f"Post: {c.get('post_title','')[:80]}]:\n"
            f"{c['content'][:600]}\n"
        )

    if high_tier:
        detail_instructions = """
OUTPUT FORMAT FOR QUALIFYING COMMENTS (high-attention batch — richer context):

recommendation: One punchy CEO-skimmable line: problem + where + plausible Disney action.
Strong verbs preferred (Deploy, Restore, Add, Fix, Reprice, Clarify, Pilot, Staff).
Scoped Monitor / Investigate / Evaluate is OK if venue + window are explicit.

context_paragraph: 3-5 tight sentences for a VP brief — what happened, lever, guest impact,
why it matters. No filler; every sentence must add operational detail from the comment.

supporting_quotes: 2-3 short quotes (under 20 words) with operational detail, not pure venting.

context_bullet: null
source_quote: null
"""
    else:
        detail_instructions = """
OUTPUT FORMAT FOR QUALIFYING COMMENTS:

recommendation: One punchy line a CEO could skim: problem + where + what Disney could do.
Prefer a strong verb; scoped Monitor / Investigate is OK when location/system is explicit.

context_bullet: One sentence naming the specific root cause or operational detail from the comment.

source_quote: Most operationally specific quote (under 20 words).

context_paragraph: null
supporting_quotes: []
"""

    prompt = f"""
You are a senior strategy analyst surfacing guest intelligence for Disney Experiences (Elias).
Goal: **succinct, actionable lines of sight** for leadership — not Reddit fluff — with **healthy recall**:
in a typical batch, a **meaningful minority** (often ~10-25%%) may qualify when they clear the rubric.
Do **not** aim for "almost nothing passes."

INTERNAL RUBRIC — holistically assign **rubric_total** 0-10:
- **Specificity** (0-3): named attraction, land, hotel, app flow, process, or role.
- **Disney lever** (0-3): Disney could act via ops, staffing, design, comms, pricing, or maintenance.
  Only reject guest-chaos cases when there is **no** plausible Disney response (signage, queue design,
  scripts, capacity, policy still count as levers).
- **Headline actionability** (0-2): a VP could assign a next step from your recommendation.
- **Signal vs noise** (0-2): not mainly a joke/meme/pure drama with **zero** ops hook.

**evidence_confidence** (one):
- "pattern" — recurrence language ("always", "every time", "still", multiple visits, etc.)
- "recurring" — hint others affected / repeats, not fully proven
- "anecdotal" — N=1 but specific enough to surface (**allowed** — early warning)

**insight_tier** (one):
- "strategic" — boardroom-grade: strong specificity + clear lever + exec-brief worthy
- "operational" — useful ops pulse; narrower, softer, or early signal

Set **is_insightful** true when rubric_total >= 5 and the row is not pure entertainment/meme noise.

HARD REJECT (keep rubric_total 0-3 / is_insightful false):
- Pure viral story / joke / drama with **no** operational hook.
- Zero named place or system (could be any park anywhere).
- No imaginable Disney action.

CATEGORY — exactly one:
imagineering | operations | maintenance | commercial | guest_services | risk

SENTIMENT: positive | negative | neutral

{detail_instructions}

Return ONLY a valid JSON array with one object per comment (every comment_number):
[
  {{
    "comment_number": 1,
    "is_insightful": true or false,
    "rubric_total": 0-10,
    "insight_tier": "strategic" or "operational" or null,
    "evidence_confidence": "pattern" or "recurring" or "anecdotal" or null,
    "category": "...",
    "sentiment": "...",
    "recommendation": "headline or null",
    "context_paragraph": "paragraph or null",
    "context_bullet": "sentence or null",
    "source_quote": "quote or null",
    "supporting_quotes": []
  }}
]

Comments to analyze:
{comment_list}

Return ONLY the JSON array. No preamble, markdown, or extra text.
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
    return None


# ── PASS 2: Borderline only — default ACCEPT ────────────────────────────────
def second_pass_borderline(comment: dict, score: dict):
    """Used only for rubric 4–6.9. Reject only clear noise; default survives."""
    prompt = f"""
This Reddit comment received a **borderline** insight score for a Disney executive dashboard (Elias).

**Default: survives: true.** Approve unless it is **clearly** unsuitable.

Reject (**survives: false**) ONLY if:
- It is mainly a joke, meme, relationship drama, or story with **no** operational hook, OR
- The "recommendation" is empty fluff with **no** named place/system and **no** plausible Disney action.

Do **not** reject for being anecdotal (N=1): early single-guest signals are allowed.

Original comment:
{comment['content'][:600]}

Proposed headline:
{score.get('recommendation', '')}

Context:
{score.get('context_paragraph') or score.get('context_bullet') or ''}

Respond with ONLY JSON:
{{
  "survives": true or false,
  "rejection_reason": "short reason if false, else null"
}}
"""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=220,
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return bool(result.get("survives", True)), result.get("rejection_reason")
        except Exception as e:
            print(f"  Pass 2 attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)

    return True, None


def insert_insight_row(payload: dict) -> bool:
    """Insert insight; drop optional columns if Supabase schema lacks them."""
    try:
        supabase.table("insights").insert(payload).execute()
        return True
    except Exception as e:
        err = str(e).lower()
        if "insight_tier" in err or "evidence_confidence" in err or "column" in err:
            slim = {k: v for k, v in payload.items() if k not in ("insight_tier", "evidence_confidence")}
            try:
                supabase.table("insights").insert(slim).execute()
                return True
            except Exception as e2:
                print(f"  Error saving insight: {e2}")
                return False
        print(f"  Error saving insight: {e}")
        return False


def process_unscored_comments():
    insights_found  = 0
    pass2_rejected  = 0
    processed_count = 0
    batch_size      = 20
    page_size       = 100  # FIX 1: Pull in small chunks, not everything at once
    page            = 0

    print("\nProcessing comments in streaming chunks...")

    while True:
        # FIX 1: Fetch one page at a time, process it immediately, then fetch the next
        result = supabase.table("raw_comments")\
            .select("*")\
            .eq("processed", False)\
            .range(page * page_size, (page + 1) * page_size)\
            .execute()

        page_comments = result.data or []

        if not page_comments:
            break  # No more unprocessed comments

        print(f"\n--- Page {page + 1}: {len(page_comments)} comments ---")

        # Build upvote list for percentile within this page
        # (same logic as before, scoped to the current page batch)
        all_upvotes = [c.get('upvotes', 0) or 0 for c in page_comments]

        def get_percentile(upvotes):
            if not all_upvotes:
                return 50.0
            rank = sum(u <= upvotes for u in all_upvotes)
            return round((rank / len(all_upvotes)) * 100, 1)

        for i in range(0, len(page_comments), batch_size):
            batch = page_comments[i:i + batch_size]

            high_batch     = [c for c in batch if get_percentile(c.get('upvotes', 0) or 0) >= 75]
            standard_batch = [c for c in batch if get_percentile(c.get('upvotes', 0) or 0) < 75]

            print(f"\n  Batch {i//batch_size + 1}: {len(high_batch)} high tier, {len(standard_batch)} standard")

            all_scored = []

            if high_batch:
                scores = score_batch(high_batch, high_tier=True)
                if scores:
                    for j, score in enumerate(scores):
                        if j < len(high_batch):
                            all_scored.append((high_batch[j], score, True))
                else:
                    print("  High tier batch failed — marking processed and skipping")
                    for c in high_batch:
                        # FIX 2: Mark processed immediately even on failure
                        supabase.table("raw_comments").update({"processed": True}).eq("id", c['id']).execute()
                        processed_count += 1

            if standard_batch:
                scores = score_batch(standard_batch, high_tier=False)
                if scores:
                    for j, score in enumerate(scores):
                        if j < len(standard_batch):
                            all_scored.append((standard_batch[j], score, False))
                else:
                    print("  Standard batch failed — marking processed and skipping")
                    for c in standard_batch:
                        # FIX 2: Mark processed immediately even on failure
                        supabase.table("raw_comments").update({"processed": True}).eq("id", c['id']).execute()
                        processed_count += 1

            for comment, score, is_high in all_scored:
                subreddit  = comment.get('subreddit', '')
                post_title = comment.get('post_title', '')
                content    = comment.get('content', '')

                # FIX 2: Mark processed IMMEDIATELY after scoring, before any insert attempt.
                # This prevents duplicate scoring if the script crashes mid-run.
                try:
                    supabase.table("raw_comments")\
                        .update({"processed": True})\
                        .eq("id", comment['id'])\
                        .execute()
                except Exception as e:
                    print(f"  Warning: failed to mark processed for {comment['id']}: {e}")

                processed_count += 1

                decision, gate_reason = rubric_pass_decision(score)
                if decision == "reject":
                    print(f"  discarded ({gate_reason}, rubric={_safe_float(score.get('rubric_total'), 0):.1f})")
                    continue

                if decision == "borderline":
                    survives, rejection_reason = second_pass_borderline(comment, score)
                    if not survives:
                        pass2_rejected += 1
                        print(f"  x [pass 2 borderline reject] {rejection_reason}")
                        continue

                experience = infer_experience(subreddit, content, post_title)
                project_tags = assign_project_tags(content, post_title)
                percentile = get_percentile(comment.get('upvotes', 0) or 0)
                insight_tier = score.get("insight_tier") or "operational"
                if insight_tier not in ("strategic", "operational"):
                    insight_tier = "operational"
                featured = (insight_tier == "strategic" and percentile >= 75) or (
                    percentile >= 88
                )
                weighted = max(comment.get('upvotes', 0) or 0, 1)
                rubric_val = _safe_float(score.get('rubric_total'), 5.0)
                tier_label = "HIGH" if is_high else "STD"
                ev = score.get("evidence_confidence") or "anecdotal"
                if ev not in ("pattern", "recurring", "anecdotal"):
                    ev = "anecdotal"

                print(
                    f"  [INSIGHT] [{tier_label}] {score.get('category','?')} | "
                    f"rubric {rubric_val:.1f} | {insight_tier} | {score.get('recommendation', '')[:72]}..."
                )

                try:
                    existing = supabase.table("insights")\
                        .select("id")\
                        .eq("raw_comment_id", comment['id'])\
                        .execute()
                    if existing.data:
                        print(f"  skipped (already has insight)")
                        continue
                except Exception as e:
                    print(f"  Dedup check error: {e} — proceeding with insert")

                payload = {
                    "raw_comment_id": comment['id'],
                    "experience_tag": experience,
                    "category_tag": score.get('category') or 'operations',
                    "recommendation": score.get('recommendation'),
                    "context_paragraph": score.get('context_paragraph'),
                    "context_bullet": score.get('context_bullet'),
                    "source_quote": score.get('source_quote'),
                    "supporting_quotes": score.get('supporting_quotes') or [],
                    "insight_quality_score": rubric_val,
                    "upvotes": comment.get('upvotes', 0),
                    "upvote_percentile": percentile,
                    "featured": featured,
                    "weighted_score": weighted,
                    "sentiment": score.get('sentiment', 'neutral'),
                    "project_tags": project_tags,
                    "username": comment.get('username'),
                    "date_posted": comment.get('date_posted'),
                    "comment_url": comment.get('comment_url'),
                    "week_number": 1,
                    "insight_tier": insight_tier,
                    "evidence_confidence": ev,
                }
                if insert_insight_row(payload):
                    insights_found += 1

        page += 1

    print(f"\n{'='*50}")
    print(f"Done. {insights_found} insights from {processed_count} comments")
    print(f"Pass 2 rejections: {pass2_rejected}")
    if processed_count > 0:
        print(f"Signal rate: {round(insights_found/processed_count*100,1)}%")
        if (insights_found + pass2_rejected) > 0:
            rejection_rate = round(pass2_rejected / (insights_found + pass2_rejected) * 100, 1)
            print(f"Pass 2 rejection rate: {rejection_rate}% of pass-1 approvals")

    return processed_count


# ── Main loop ─────────────────────────────────────────────────────────────────
processed = process_unscored_comments()

# FIX 3: Safe retry loop — bail out if no progress is being made
MAX_RETRIES = 3
retries_without_progress = 0

while True:
    result = supabase.table("raw_comments").select("id", count="exact").eq("processed", False).execute()
    remaining = result.count or 0

    if remaining == 0:
        print("\nAll comments processed!")
        break

    print(f"\n{remaining} still unprocessed — retrying in 10 seconds...")
    time.sleep(10)

    newly_processed = process_unscored_comments()

    if newly_processed == 0:
        retries_without_progress += 1
        print(f"  No progress made ({retries_without_progress}/{MAX_RETRIES} retries)")
        if retries_without_progress >= MAX_RETRIES:
            print(f"  No progress after {MAX_RETRIES} retries — stopping to avoid infinite loop.")
            print(f"  {remaining} comments may have failed permanently. Check logs.")
            break
    else:
        retries_without_progress = 0  # Reset counter if progress was made