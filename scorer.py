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
OUTPUT FORMAT FOR QUALIFYING COMMENTS:

recommendation: A razor-sharp headline naming the exact fix, the exact
location, and the exact problem. Starts with a concrete action verb
(Deploy, Restore, Redesign, Restaff, Reprice, Add, Remove, Fix).
Never starts with Investigate, Enhance, Consider, Review, or Improve.

Bad: "Investigate guest treatment during bathroom emergencies at Splash Mountain"
Bad: "Enhance staff protocols for addressing guest emergencies"
Good: "Deploy bathroom break cast members at Splash Mountain queue
      exit to actively offer line-hold assistance to families with children"
Good: "Restore the second Fantasmic parade to stagger the Rivers of
      America bridge exit — guests report 40+ minute post-show waits
      since its 2022 elimination"

context_paragraph: 3-5 sentences that read like a VP briefing note.
Explain what is specifically happening, what the root cause appears to be,
what the guest impact is, and why this matters strategically. Reference
specific details from the comment. No filler. No generic observations.
Every sentence must add information a Disney exec could not have inferred
without reading this specific comment.

supporting_quotes: 2-3 direct quotes under 15 words each that are
specific and striking — not emotional reactions, but observations that
contain operational detail.

context_bullet: null
source_quote: null
"""
    else:
        detail_instructions = """
OUTPUT FORMAT FOR QUALIFYING COMMENTS:

recommendation: A razor-sharp headline naming the exact fix, the exact
location, and the exact problem. Starts with a concrete action verb.
Never starts with Investigate, Enhance, Consider, Review, or Improve.

context_bullet: One sentence naming the specific root cause or operational
detail that makes this finding actionable. Must add information beyond
the headline. Must reference something concrete from the comment.

source_quote: The single most operationally specific quote from the
comment under 15 words. Not an emotional reaction — a factual observation.

context_paragraph: null
supporting_quotes: []
"""

    prompt = f"""
You are a senior strategy analyst briefing Disney's executive leadership.
Your job is to find comments containing intelligence that would change
what a Disney VP does on Monday morning.

You are extremely selective. You are looking for 1 in 30 comments at most.
Most comments — even interesting, high-upvote ones — do not qualify.
When in doubt, the answer is always reject.

THE CORE TEST — ask this before approving any comment:
"If I showed this to a Disney VP, would they know exactly what
operational or strategic action to take, and where?"
If the answer is anything other than an immediate yes — reject it.

HARD DISQUALIFIERS — reject instantly if any are true:

1. VIRAL STORY: The comment got upvotes because it is entertaining,
   relatable, funny, or emotionally resonant — not because it contains
   actionable intelligence. Ask: would this make r/tifu or r/AmItheAsshole?
   If yes, reject it. Bathroom stories, parenting fails, funny cast member
   moments — these are stories, not intelligence.

2. GUEST BEHAVIOR PROBLEM: The issue is caused by other guests, not by
   Disney's systems, staffing, or design. Disney cannot fix bad parenting,
   rude guests, or children licking handrails. Reject any comment where
   the root cause is guest behavior rather than Disney operations.

3. BANNED RECOMMENDATION WORDS: If the only honest recommendation starts
   with Investigate, Enhance, Consider, Review, Look into, or Improve —
   reject it. These mean the comment lacks enough specificity to be
   actionable. A real finding has a real fix, not a study.

4. GENERIC: The finding contains no specific detail that couldn't be
   written by someone who has never visited. If it could appear in any
   generic theme park review — reject it. Specificity is required:
   a named attraction, a named system, a named location, a specific time
   or date pattern, or a specific staff role.

5. ONE-TIME INCIDENT: A single bad experience with no signal it is
   systemic. One broken animatronic seen once is not intelligence.
   Reject unless the comment contains language suggesting recurrence:
   "every time", "always", "still broken", "third visit", "multiple
   people", "everyone was", or similar pattern indicators.

6. NO CLEAR FIX: The problem described has no operational solution Disney
   could implement. Reject if you cannot write a concrete action verb
   recommendation that names a specific change at a specific location.

WHAT QUALIFIES — all must be true:
- Names a specific system, location, attraction, or staff role
- The problem is caused by Disney's design, staffing, or operations
- There is a concrete fix Disney could implement
- The recommendation can start with a real action verb naming the fix
- A Disney ops manager would know exactly what to go look at
- Contains detail that could not be inferred without this specific comment

CATEGORY — assign exactly one:
- imagineering: Specific new creative concept that does not exist yet
- operations: Specific failure in crowd flow, wait times, cast member
  behavior, app, food service, signage, or queue management
- maintenance: Specific physical deterioration at a named location
- commercial: Specific pricing, revenue, or merchandise finding with data
- guest_services: Specific hotel, accessibility, or loyalty service failure
- risk: Specific safety or legal exposure Disney could act on immediately

SENTIMENT:
- positive: Specific constructive praise or suggestion
- negative: Specific criticism or failure
- neutral: Factual observation

{detail_instructions}

Return ONLY a valid JSON array, one object per comment:
[
  {{
    "comment_number": 1,
    "is_insightful": true or false,
    "category": "one of the six categories",
    "sentiment": "positive or negative or neutral",
    "recommendation": "concrete action verb headline or null",
    "context_paragraph": "VP briefing paragraph or null",
    "context_bullet": "one specific detail sentence or null",
    "source_quote": "most operationally specific quote under 15 words or null",
    "supporting_quotes": ["quote 1", "quote 2", "quote 3"]
  }}
]

Comments to analyze:
{comment_list}

Return ONLY the JSON array. No preamble, no markdown, no explanation.
Expect to mark the vast majority of comments is_insightful: false.
You are looking for genuine operational intelligence, not interesting stories.
When in doubt — reject.
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


# ── PASS 2: Rejection filter ──────────────────────────────────────────────────
def second_pass_filter(comment, score):
    """
    Re-evaluates a single comment that passed Pass 1.
    Asks a harder adversarial question: find the reason to reject this.
    Returns True if the comment survives (still insightful), False if rejected.
    """
    prompt = f"""
You are a brutally skeptical editor reviewing an insight that a junior
analyst flagged as actionable for Disney's executive team.

Your job is to find the reason to REJECT it. You are looking for any of
these failure modes:

1. VIRAL STORY THAT SLIPPED THROUGH: It passed because it has a specific
   location or action verb, but the underlying reason it got upvotes is
   that it is entertaining or relatable — not operationally useful.

2. ANECDOTE DRESSED AS PATTERN: It uses specific language but describes
   a single personal experience. There is no evidence this is systemic.
   One person's bad experience is not a Disney operations problem.

3. RECOMMENDATION IS HOLLOW: The action verb recommendation sounds
   concrete but actually just restates the complaint. A real recommendation
   must describe a change to a system, process, staffing model, or physical
   space — not just "fix the thing that was broken."

4. ALREADY OBVIOUS: Disney leadership unambiguously already knows and
   tracks this. Every park operator knows queues back up at closing.
   Every hotel knows check-in can be slow. Reject if there is nothing
   here a Disney VP would not already have in their weekly ops report.

5. VAGUE DESPITE APPEARING SPECIFIC: It names a location but the actual
   problem and fix are generic. "Space Mountain queue needs better
   signage" could apply to any attraction at any theme park anywhere.

The original comment:
{comment['content'][:600]}

The analyst's proposed recommendation:
{score.get('recommendation', '')}

The analyst's reasoning (context):
{score.get('context_paragraph') or score.get('context_bullet') or ''}

Respond with ONLY a JSON object:
{{
  "survives": true or false,
  "rejection_reason": "one sentence explaining why it was rejected, or null if it survives"
}}

Return ONLY the JSON. No preamble, no explanation.
Default to rejecting — only mark survives: true if you genuinely cannot
find a valid reason to reject it.
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return result.get("survives", False), result.get("rejection_reason")
        except Exception as e:
            print(f"  Pass 2 attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)

    # If pass 2 fails entirely, default to keeping the insight
    # (better to let one through than silently lose data)
    return True, None


def calculate_percentile(upvotes, all_upvotes):
    if not all_upvotes:
        return 50.0
    rank = sum(u <= upvotes for u in all_upvotes)
    return round((rank / len(all_upvotes)) * 100, 1)


def process_unscored_comments():
    print("\nPulling unprocessed comments...")

    all_comments = []
    page = 0
    page_size = 1000
    while True:
        result = supabase.table("raw_comments")\
            .select("*")\
            .eq("processed", False)\
            .range(page * page_size, (page + 1) * page_size - 1)\
            .execute()
        batch = result.data or []
        all_comments.extend(batch)
        if len(batch) < page_size:
            break
        page += 1

    comments = all_comments
    total = len(comments)
    print(f"Found {total} unprocessed comments\n")

    if not comments:
        print("Nothing to process.")
        return

    posts = {}
    for c in comments:
        pid = c.get('post_id', 'unknown')
        if pid not in posts:
            posts[pid] = []
        posts[pid].append(c)

    insights_found   = 0
    pass2_rejected   = 0
    processed_count  = 0
    batch_size       = 20

    for post_id, post_comments in posts.items():
        all_upvotes = [c.get('upvotes', 0) or 0 for c in post_comments]

        def get_percentile(upvotes):
            if not all_upvotes:
                return 50.0
            rank = sum(u <= upvotes for u in all_upvotes)
            return round((rank / len(all_upvotes)) * 100, 1)

        for i in range(0, len(post_comments), batch_size):
            batch = post_comments[i:i + batch_size]

            high_batch     = [c for c in batch if get_percentile(c.get('upvotes', 0) or 0) >= 75]
            standard_batch = [c for c in batch if get_percentile(c.get('upvotes', 0) or 0) < 75]

            pct_done = round((processed_count / total) * 100, 1)
            print(f"\n[{pct_done}%] Post {post_id[:8]}... — {len(high_batch)} high tier, {len(standard_batch)} standard")

            all_scored = []

            if high_batch:
                scores = score_batch(high_batch, high_tier=True)
                if scores:
                    for j, score in enumerate(scores):
                        if j < len(high_batch):
                            all_scored.append((high_batch[j], score, True))
                else:
                    print("  High tier batch failed after retries — skipping")
                    for c in high_batch:
                        supabase.table("raw_comments").update({"processed": True}).eq("id", c['id']).execute()
                        processed_count += 1

            if standard_batch:
                scores = score_batch(standard_batch, high_tier=False)
                if scores:
                    for j, score in enumerate(scores):
                        if j < len(standard_batch):
                            all_scored.append((standard_batch[j], score, False))
                else:
                    print("  Standard batch failed after retries — skipping")
                    for c in standard_batch:
                        supabase.table("raw_comments").update({"processed": True}).eq("id", c['id']).execute()
                        processed_count += 1

            for comment, score, is_high in all_scored:
                subreddit  = comment.get('subreddit', '')
                post_title = comment.get('post_title', '')
                content    = comment.get('content', '')

                if not score.get('is_insightful'):
                    print(f"  discarded (pass 1)")

                else:
                    # ── PASS 2: adversarial rejection filter ──────────────────
                    survives, rejection_reason = second_pass_filter(comment, score)

                    if not survives:
                        pass2_rejected += 1
                        print(f"  ✗ [pass 2 rejected] {rejection_reason}")

                    else:
                        experience   = infer_experience(subreddit, content, post_title)
                        project_tags = assign_project_tags(content, post_title)
                        percentile   = get_percentile(comment.get('upvotes', 0) or 0)
                        featured     = percentile >= 75
                        weighted     = max(comment.get('upvotes', 0) or 0, 1)
                        tier_label   = "HIGH" if is_high else "STD"

                        print(f"  ✓ [{tier_label}] {score['category']} | {score.get('recommendation','')[:80]}...")

                        # Guard: skip if this raw_comment already has an insight
                        # (safety net before the Supabase unique constraint fires)
                        try:
                            existing = supabase.table("insights") \
                                .select("id") \
                                .eq("raw_comment_id", comment['id']) \
                                .execute()
                            if existing.data:
                                print(f"  skipped (raw_comment_id already has insight)")
                                processed_count += 1
                                continue
                        except Exception as e:
                            print(f"  Dedup check error: {e} — proceeding with insert")

                        try:
                            supabase.table("insights").insert({
                                "raw_comment_id":        comment['id'],
                                "experience_tag":        experience,
                                "category_tag":          score['category'],
                                "recommendation":        score.get('recommendation'),
                                "context_paragraph":     score.get('context_paragraph'),
                                "context_bullet":        score.get('context_bullet'),
                                "source_quote":          score.get('source_quote'),
                                "supporting_quotes":     score.get('supporting_quotes', []),
                                "insight_quality_score": 10.0,
                                "upvotes":               comment.get('upvotes', 0),
                                "upvote_percentile":     percentile,
                                "featured":              featured,
                                "weighted_score":        weighted,
                                "sentiment":             score.get('sentiment', 'neutral'),
                                "project_tags":          project_tags,
                                "username":              comment.get('username'),
                                "date_posted":           comment.get('date_posted'),
                                "comment_url":           comment.get('comment_url'),
                                "week_number":           1
                            }).execute()
                            insights_found += 1
                        except Exception as e:
                            print(f"  Error saving: {e}")

                try:
                    supabase.table("raw_comments")\
                        .update({"processed": True})\
                        .eq("id", comment['id'])\
                        .execute()
                except Exception as e:
                    print(f"  Error marking processed: {e}")

                processed_count += 1

    print(f"\n{'='*50}")
    print(f"Done. {insights_found} insights from {processed_count} comments")
    print(f"Pass 2 rejections: {pass2_rejected}")
    if processed_count > 0:
        print(f"Signal rate: {round(insights_found/processed_count*100,1)}%")
        if (insights_found + pass2_rejected) > 0:
            rejection_rate = round(pass2_rejected / (insights_found + pass2_rejected) * 100, 1)
            print(f"Pass 2 rejection rate: {rejection_rate}% of pass-1 approvals")


process_unscored_comments()

while True:
    result = supabase.table("raw_comments").select("id", count="exact").eq("processed", False).execute()
    remaining = result.count or 0
    if remaining == 0:
        print("\nAll comments processed!")
        break
    print(f"\n{remaining} still unprocessed — retrying in 10 seconds...")
    time.sleep(10)
    process_unscored_comments()