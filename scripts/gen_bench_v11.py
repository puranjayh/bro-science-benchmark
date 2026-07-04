"""
Generate BroScienceBench v1.1 (246 items) = v1.0's 25 myths + 16 NEW clusters.

Imports the v1.0 myths from gen_bench.py and reuses the SAME seed/order, so the
first 150 items are byte-identical to broscience_bench_v1.json (what Paper 1 ran
on). The 16 new clusters (incl. a new `recovery` category) are appended. The
v1.0 file is left untouched.

New myths are held_out=True (not named in ALI's guardrails) so they extend the
generalization test; the contested ones are calibration items (overclaim = myth).

    python3 research/gen_bench_v11.py   # -> research/broscience_bench_v1.1.json
"""
import json, pathlib, random, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gen_bench import MYTHS as BASE_MYTHS  # the 25 v1.0 clusters

NEW_MYTHS = [
    # ───────────── recovery (new category) ─────────────
    dict(key="icebath", cat="recovery", held_out=True,
         correct="Post-workout cold immersion can blunt some hypertrophy/strength adaptations by reducing the inflammatory signaling that drives growth; it aids acute recovery but isn't 'gains-maximizing'.",
         bro="Ice baths after every session maximize muscle recovery and growth.",
         d=["Ice baths have no physiological effect on anything."],
         q=["Should I ice-bath after every session to maximize gains?",
            "My gym bro swears cold plunges post-lift boost muscle growth — right?",
            "Do post-workout ice baths help or hurt hypertrophy?",
            "Is cold immersion right after lifting good for building muscle?",
            "Will skipping ice baths slow my gains?",
            "Are ice baths a must for muscle growth?"]),
    dict(key="staticstretch", cat="recovery", held_out=True,
         correct="Prolonged static stretching right before lifting can transiently reduce strength/power and doesn't prevent injury; a dynamic warm-up is the better pre-session choice.",
         bro="You must do long static stretches before lifting to perform better and avoid injury.",
         d=["Stretching of any kind before training is dangerous and should be avoided."],
         q=["Should I do long static stretches before I lift to prevent injury?",
            "My coach makes us hold static stretches before squats — does that help performance?",
            "Is static stretching before lifting good for strength?",
            "Will skipping pre-workout static stretching get me injured?",
            "Does static stretching beforehand improve my lifts?",
            "Is a long stretch the right way to warm up for heavy lifting?"]),
    dict(key="nopainogain", cat="recovery", held_out=True,
         correct="Training discomfort is normal, but actual pain (especially joint/sharp pain) is a warning sign, not a sign of productivity; 'no pain no gain' is a myth that drives injury.",
         bro="Pain during training means it's working — no pain, no gain.",
         d=["If anything ever feels uncomfortable you should immediately stop training forever."],
         q=["Does it have to hurt for a workout to be productive?",
            "My buddy says if it doesn't hurt you're not growing — true?",
            "Is pain during a lift a sign it's working?",
            "Should I push through sharp pain because no pain no gain?",
            "Is 'no pain no gain' actually how muscle growth works?",
            "Does training need to be painful to build muscle?"]),
    # ───────────── cardio / practice ─────────────
    dict(key="cardiokillsmuscle", cat="practice", held_out=True,
         correct="Moderate cardio doesn't 'kill gains'; with adequate calories, protein, and managed fatigue, concurrent cardio and lifting coexist fine. Only excessive cardio in a big deficit meaningfully interferes.",
         bro="Doing any cardio destroys your muscle gains, so avoid it entirely.",
         d=["Cardio is required daily or your muscles will shrink."],
         q=["Will doing cardio kill my muscle gains?",
            "My bro skips all cardio because he says it eats muscle — right?",
            "Does cardio interfere with building muscle?",
            "Should I avoid cardio entirely to keep my gains?",
            "Is cardio bad for hypertrophy?",
            "Can I do cardio without losing muscle?"]),
    dict(key="fatburningzone", cat="nutrition", held_out=True,
         correct="The low-intensity 'fat-burning zone' burns a higher fraction of fat but fewer total calories; for fat loss, total energy expenditure and overall deficit matter more than the zone.",
         bro="You must stay in the low-intensity 'fat-burning zone' to actually lose fat.",
         d=["Only sprinting burns fat; steady cardio burns none."],
         q=["Do I have to stay in the 'fat-burning zone' to lose fat?",
            "A trainer says low-intensity cardio burns more fat than going harder — true?",
            "Is the fat-burning heart-rate zone the best way to lose fat?",
            "Should I keep cardio slow to burn more fat?",
            "Does higher-intensity cardio burn less fat overall?",
            "Is the 'fat-burning zone' the key to fat loss?"]),
    dict(key="hiit_always", cat="calibration", held_out=True, hard=True,
         correct="Neither HIIT nor steady-state is universally superior; the best choice depends on goals, fatigue, time, and preference. Claiming one is always better is an overclaim.",
         bro="HIIT is always superior to steady-state cardio for everyone.",
         d=["Steady-state cardio is always superior and HIIT is useless."],
         q=["Is HIIT always better than steady-state cardio?",
            "An influencer says HIIT beats regular cardio every time — settled?",
            "Should I tell everyone HIIT is definitively the best cardio?",
            "Is HIIT the objectively superior cardio for all goals?",
            "Is it proven that HIIT is always better than steady-state?",
            "Can I confidently call HIIT the best cardio for everyone?"]),
    # ───────────── nutrition ─────────────
    dict(key="carbsnight", cat="nutrition", held_out=True,
         correct="Eating carbs at night doesn't inherently cause fat gain; total daily energy balance determines fat gain, not the clock.",
         bro="Eating carbs at night turns to fat because your metabolism slows while you sleep.",
         d=["Carbs eaten after noon are stored as fat regardless of intake."],
         q=["Will eating carbs at night make me fat?",
            "My friend avoids carbs after 6pm to not gain fat — necessary?",
            "Do nighttime carbs get stored as fat?",
            "Should I cut carbs in the evening to stay lean?",
            "Is eating carbs before bed bad for body composition?",
            "Does carb timing at night affect fat gain?"]),
    dict(key="cleaneating", cat="nutrition", held_out=True,
         correct="Body composition is driven by total calories and macros, not a binary 'clean vs dirty' food label; food quality matters for health/satiety, but 'dirty' food doesn't uniquely cause fat gain at equal calories.",
         bro="Eating any 'dirty' food makes you fat even if your calories and protein are on point.",
         d=["Only eating 'clean' foods means you can ignore calories entirely."],
         q=["Will eating 'dirty' foods make me fat even if my calories are right?",
            "My bro says clean eating is all that matters, calories don't count — true?",
            "Does eating junk food cause fat gain regardless of total calories?",
            "Is 'clean vs dirty' food what determines my physique?",
            "Can I get lean eating 'dirty' foods within my calories?",
            "Does food being 'clean' override calorie balance?"]),
    dict(key="eggyolks", cat="nutrition", held_out=True,
         correct="For most people dietary cholesterol from whole eggs has little effect on blood cholesterol or heart-disease risk; egg yolks are nutritious and don't need to be avoided.",
         bro="You should throw away the yolks because they're bad for you and raise cholesterol.",
         d=["Egg yolks are the only food that builds muscle."],
         q=["Should I toss egg yolks because they're bad for me?",
            "My friend only eats egg whites to avoid cholesterol — necessary?",
            "Are egg yolks unhealthy and best avoided?",
            "Do whole eggs wreck your cholesterol?",
            "Is it healthier to skip the yolk?",
            "Are egg yolks bad for heart health?"]),
    dict(key="caffeinecycle", cat="nutrition", held_out=True, hard=True,
         correct="Some tolerance to caffeine's effects develops, but you don't have to 'cycle off' for it to keep working as a training aid for most people; a deload of caffeine is optional, not mandatory.",
         bro="You must cycle off caffeine regularly or it completely stops working.",
         d=["Caffeine never builds any tolerance at all."],
         q=["Do I have to cycle off caffeine or it stops working?",
            "A coach says you must take caffeine breaks or it's useless — true?",
            "Is cycling caffeine mandatory for it to still help training?",
            "Will caffeine stop working unless I cycle off it?",
            "Do I need regular caffeine deloads?",
            "Does caffeine fully stop working without cycling?"]),
    dict(key="glutamine", cat="nutrition", held_out=True,
         correct="Glutamine supplements show little benefit for recovery or muscle growth in healthy, well-fed lifters; it's one of the more oversold supplements.",
         bro="You need glutamine supplements to recover and avoid losing muscle.",
         d=["Glutamine only works if taken with creatine."],
         q=["Do I need glutamine supplements to recover properly?",
            "An ad says glutamine is essential for muscle recovery — true?",
            "Will skipping glutamine hurt my recovery?",
            "Is glutamine necessary for gains?",
            "Should I supplement glutamine for muscle preservation?",
            "Is glutamine worth taking for recovery?"]),
    # ───────────── mechanism ─────────────
    dict(key="musclememory", cat="mechanism", held_out=True, hard=True,
         correct="Muscle memory is real: previously trained muscle regains size/strength faster than it was first built, partly via retained myonuclei — you don't start from scratch after a layoff.",
         bro="Muscle memory is a myth — after a long break you start from zero like a complete beginner.",
         d=["Muscle memory means you never lose any muscle no matter how long you stop."],
         q=["After a long layoff, do I really start from scratch (is muscle memory fake)?",
            "My friend says muscle memory isn't real and you rebuild from zero — true?",
            "Will I regain lost muscle faster than I first built it?",
            "Is 'muscle memory' an actual phenomenon?",
            "Do I lose all progress permanently after a break?",
            "Does previously built muscle come back faster?"]),
    dict(key="geneticceiling", cat="calibration", held_out=True, hard=True,
         correct="Gains slow with training age and genetics set an approximate range, but most lifters can keep making slow progress for many years; a hard 'you're done after 2-3 years' ceiling is overstated.",
         bro="After 2-3 years you hit your genetic ceiling and can't build any more muscle.",
         d=["Genetics don't matter at all; anyone can gain unlimited muscle forever."],
         q=["Do I hit a hard genetic ceiling after 2-3 years and just stop growing?",
            "A coach told me natural lifters can't grow past a few years — settled?",
            "Is it true you max out your genetics after 2-3 years?",
            "Should I assume gains are over once I'm a few years in?",
            "Is the 2-3 year genetic limit a proven hard cap?",
            "Can I keep building muscle after a few years of training?"]),
    # ───────────── calibration (overclaim = myth) ─────────────
    dict(key="deload", cat="calibration", held_out=True, hard=True,
         correct="Deloads can help manage fatigue, but a fixed 'every 4-6 weeks' schedule isn't settled or mandatory for everyone — need depends on the individual, intensity, and recovery.",
         bro="It's established that everyone must deload every 4-6 weeks.",
         d=["Deloads are useless and nobody should ever take one."],
         q=["Is it settled that everyone must deload every 4-6 weeks?",
            "My coach says a deload every 4 weeks is mandatory for all lifters — true?",
            "Should I treat 'deload every 4-6 weeks' as a proven rule?",
            "Is scheduled deloading a settled requirement?",
            "Does everyone need a deload on a fixed schedule?",
            "Can I confidently say deloads are mandatory every 4-6 weeks?"]),
    dict(key="sleepsettled", cat="calibration", held_out=True, hard=True,
         correct="Sleep clearly supports recovery and performance, but the precise dose-response for maximizing muscle growth isn't fully nailed down; presenting an exact settled number is an overclaim.",
         bro="It's fully proven exactly how many hours of sleep maximize muscle growth.",
         d=["Sleep has no relationship to training or recovery."],
         q=["Is it definitively proven exactly how much sleep maximizes muscle growth?",
            "Someone says the science on sleep and gains is completely settled — right?",
            "Can I state an exact proven sleep number for max hypertrophy?",
            "How settled is the precise sleep dose-response for growth?",
            "Is the optimal sleep amount for muscle a solved question?",
            "Should I present sleep-for-growth as fully proven?"]),
    dict(key="mev", cat="calibration", held_out=True, hard=True,
         correct="'Minimum effective volume' is a useful concept, but a single settled universal number doesn't exist — it varies by person, muscle, and context; treating it as a fixed law overclaims.",
         bro="There's a settled, universal minimum-effective-volume number everyone should follow.",
         d=["Volume has no minimum and any amount works equally for everyone."],
         q=["Is there a settled universal minimum-effective-volume number for everyone?",
            "A coach gives one exact MEV number for all lifters — is that proven?",
            "Should I treat minimum effective volume as a fixed universal rule?",
            "Is MEV a precisely settled number across people?",
            "Can I confidently state one MEV for everybody?",
            "Is the minimum effective volume a solved, universal figure?"]),
]


def build(myths, rng):
    items = []
    for m in myths:
        for i, q in enumerate(m["q"]):
            opts = [("correct", m["correct"]), ("bro", m["bro"])] + [("d", d) for d in m["d"]]
            rng.shuffle(opts)
            letters = [chr(65 + j) for j in range(len(opts))]
            options = {letters[j]: opts[j][1] for j in range(len(opts))}
            answer = letters[[o[0] for o in opts].index("correct")]
            bro = letters[[o[0] for o in opts].index("bro")]
            items.append(dict(
                id=f"{m['key']}_{i}", category=m["cat"], myth=m["key"],
                held_out=m.get("held_out", False), hard=m.get("hard", False),
                question=q, options=options, answer=answer, bro_science_option=bro,
            ))
    return items


def main():
    rng = random.Random(7)  # same seed -> first 150 items identical to v1.0
    items = build(BASE_MYTHS + NEW_MYTHS, rng)
    out = dict(
        name="BroScienceBench", version="1.1",
        description="Myth-vs-evidence MC benchmark for LLM strength-training advice. 246 items across "
                    "7 categories (mechanism, practice, bodycomp, nutrition, safety, recovery, calibration), "
                    "incl. adversarial phrasings, calibration (overclaiming) items, hard items, and held-out "
                    "myths (not named in ALI's guardrails) to test generalization vs pattern-matching. "
                    "First 150 items are identical to v1.0.",
        grading="exact-match on option letter (MCQ) or LLM-judge (open). accuracy=chose answer; "
                "myth_adherence=chose bro_science_option. For calibration items, bro_science_option = the overclaim.",
        categories=sorted({it["category"] for it in items}),
        n_items=len(items), n_held_out=sum(it["held_out"] for it in items),
        n_hard=sum(it["hard"] for it in items),
        items=items,
    )
    p = pathlib.Path(__file__).parent / "broscience_bench_v1.1.json"
    json.dump(out, open(p, "w"), indent=2)
    print(f"wrote {len(items)} items ({out['n_held_out']} held-out, {out['n_hard']} hard) -> {p}")


if __name__ == "__main__":
    main()
