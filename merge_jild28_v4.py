#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 28 easy-Urdu tashreeh v4 chunks into jild-28.json.

Reads the 14 leaf chunk files listed in chunks-manifest-v4-jild28.json,
concatenates them in order 01 -> 02 -> ... -> 14, COMBINES the 5
two-part groups below into single items, applies the 16 rename-onlys,
STABLE SORTS by start_page (mirroring the v3 merge), derives
start_page = min(pages) where the field is absent (0 derived: all
chunks carry start_page), normalises page markers (0 present), validates,
and writes {"masail": [...]} to jild-28.json.

ORDER -- chunk order is the order, then a stable sort by start_page:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-28.json
  has ID order == stable sort by start_page of the concatenation
  (verified: the v3 order IS the stable sort, including its tied
  start_pages). Do NOT sort or reorder before the combines/renames.
  Within each chunk, items keep file order.
  CHUNK_ORDER is an explicit 14-leaf list.

COMBINES (5): parts are found BY (id, start_page) selectors, in page
  order. Every part has EMPTY sawal (risala sections, no question);
  the combined sawal stays empty. Title: the FIRST part's title,
  asserted against the embedded merged-v3 title (V3_TITLES). Jawab:
  " ".join of the stripped part jawabs — one space at the seam (every
  head ends with "۔" and every tail starts with "یہ", no space either
  side; direct concatenation would fuse the two sentences). Pages:
  sorted union. Notes: concatenation in order.
    shamama-4-nufha-3   [206-212] + [213-215] -> [206-215], 10pp
    shamama-4-nufha-14  [254-258] + [259-261] -> [254-261], 8pp
    shamama-4-nufha-21  [303] + [304-334] -> [303-334], 32pp
    zulal-shubha-1-muqaddimat [531-544] + [545-550] -> [531-550], 20pp
    zalal-nqi-radd-abu-ubayda [579-593] + [595-603] -> [579-603] minus
      gap 594, 24pp
  After the combines there are 89 items and 89 unique ids — the
  duplicate-id assertion runs AFTER the combines, not before.
RENAME-ONLY (16): the plain nafha-N ids of chunks 05/06 (lesson 535)
  move to the shamama-4-nufha-N form (nafha-4..13 @215..251, nafha-15..20
  @261..289); chunk 03's plain nafha-1..10 (lesson 533) keep their ids.
  The duplicate ids nafha-3..nafha-10 repeat across chunks 03 and 05
  for DIFFERENT items — every rename is scoped by start_page. The
  'nafhah' spelling (chunk 02, with 'h') is never normalised.
  No print-error renames were applied in the leaves.
  DO-NOT-COMBINE kept: nafhah-12 does NOT continue into chunk 03;
  shubha-3 does NOT continue into the tadhyeel [641-651]; tatimma
  [336-360] stays separate from nafha-21; masala-8 [428-431] keeps
  its plain id (no other masala-8 in the volume).
  All chunks carry start_page == min(pages) (0 derived). Pages are
  shared between items by design (a boundary page belongs to two
  items): present pages 705, unique pages 636 — every page assertion
  uses SETS.

EMPTY JAWAB: none — 0 empty jawab in the leaves and after the merge.
EMPTY SAWAL after the merge: 72 (== v3, all by design).
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild28.json"

# Concatenation order: chunk files 01 -> 14, in order.
CHUNK_ORDER = ["jild-28-chunk-01.json", "jild-28-chunk-02.json", "jild-28-chunk-03.json", "jild-28-chunk-04.json", "jild-28-chunk-05.json", "jild-28-chunk-06.json", "jild-28-chunk-07.json", "jild-28-chunk-08.json", "jild-28-chunk-09.json", "jild-28-chunk-10.json", "jild-28-chunk-11.json", "jild-28-chunk-12.json", "jild-28-chunk-13.json", "jild-28-chunk-14.json"]

EXPECTED_ITEMS = 89
EXPECTED_PAGES = 636
EXPECTED_MIN_PAGE = 5
EXPECTED_MAX_PAGE = 686
EXPECTED_VOLUME_IDS = {32}
EXPECTED_FIRST_ID = "jild28-pesh-lafz"
EXPECTED_LAST_ID = "jild28-zulal-latifa-baqillani"

# v3 ID sequence, verbatim from content/tashreeh/jild-28.json.
V3_IDS = ["jild28-pesh-lafz", "jild28-masala-1", "jild28-masala-2", "jild28-masala-3", "jild28-shamaim-al-anbar-intro", "jild28-nafhah-1", "jild28-nafhah-2", "jild28-nafhah-3", "jild28-nafhah-4", "jild28-nafhah-5", "jild28-nafhah-6", "jild28-nafhah-7", "jild28-nafhah-8", "jild28-nafhah-9", "jild28-nafhah-10", "jild28-nafhah-11", "jild28-nafhah-12", "jild28-nafha-1", "jild28-nafha-2", "jild28-nafha-3", "jild28-nafha-4", "jild28-nafha-5", "jild28-nafha-6", "jild28-nafha-7", "jild28-nafha-8", "jild28-nafha-9", "jild28-nafha-10", "jild28-shamama-3-nufha-1", "jild28-shamama-3-nufha-2", "jild28-shamama-3-nufha-3", "jild28-shamama-4-intro", "jild28-shamama-4-nufha-1", "jild28-shamama-4-nufha-2", "jild28-shamama-4-nufha-3", "jild28-shamama-4-nufha-4", "jild28-shamama-4-nufha-5", "jild28-shamama-4-nufha-6", "jild28-shamama-4-nufha-7", "jild28-shamama-4-nufha-8", "jild28-shamama-4-nufha-9", "jild28-shamama-4-nufha-10", "jild28-shamama-4-nufha-11", "jild28-shamama-4-nufha-12", "jild28-shamama-4-nufha-13", "jild28-shamama-4-nufha-14", "jild28-shamama-4-nufha-15", "jild28-shamama-4-nufha-16", "jild28-shamama-4-nufha-17", "jild28-shamama-4-nufha-18", "jild28-shamama-4-nufha-19", "jild28-shamama-4-nufha-20", "jild28-shamama-4-nufha-21", "jild28-risala-535-tatimma", "jild28-masala-4", "jild28-masala-5", "jild28-masala-6-ta-10", "jild28-masala-11", "jild28-masala-12", "jild28-masala-13", "jild28-masala-8", "jild28-deobandi-fatwa", "jild28-masala-19", "jild28-masala-20", "jild28-masala-21", "jild28-masala-22", "jild28-masala-22-doom", "jild28-zulal-intro", "jild28-zulal-muqaddima-1", "jild28-zulal-muqaddima-2", "jild28-zulal-razi-dalil", "jild28-zulal-munaqasha-1", "jild28-zulal-munaqasha-2", "jild28-zulal-shubha-1-muqaddimat", "jild28-zalal-nqi-muqaddima-3", "jild28-zalal-nqi-muqaddima-4", "jild28-zalal-nqi-muqaddima-5", "jild28-zalal-nqi-talkhis", "jild28-zalal-nqi-radd-abu-ubayda", "jild28-risala-77-shubha-2", "jild28-risala-77-shubha-3", "jild28-zulal-tadhyeel", "jild28-zulal-takmeel", "jild28-zulal-tasjeel", "jild28-zulal-wajh-thani", "jild28-zulal-wajh-thalis", "jild28-zulal-tanbih", "jild28-zulal-khatima", "jild28-zulal-latifa-layl", "jild28-zulal-latifa-baqillani"]

# v3 pages per item id, verbatim from content/tashreeh/jild-28.json.
V3_PAGES = {
    "jild28-pesh-lafz": [5, 6, 7, 8, 9, 10],
    "jild28-masala-1": [51],
    "jild28-masala-2": [51, 52],
    "jild28-masala-3": [52],
    "jild28-shamaim-al-anbar-intro": [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
    "jild28-nafhah-1": [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77],
    "jild28-nafhah-2": [77, 78, 79],
    "jild28-nafhah-3": [79, 80, 81, 82, 83, 84, 85, 86, 87, 88],
    "jild28-nafhah-4": [89, 90, 91, 92, 93],
    "jild28-nafhah-5": [93, 94, 95],
    "jild28-nafhah-6": [95, 96],
    "jild28-nafhah-7": [96, 97],
    "jild28-nafhah-8": [97, 98, 99],
    "jild28-nafhah-9": [99, 100, 101, 102, 103, 104],
    "jild28-nafhah-10": [104, 105],
    "jild28-nafhah-11": [105, 106, 107],
    "jild28-nafhah-12": [107, 108, 109, 110, 111, 112],
    "jild28-nafha-1": [113, 114, 115, 116, 117],
    "jild28-nafha-2": [117, 118, 119, 120],
    "jild28-nafha-3": [120, 121, 122],
    "jild28-nafha-4": [122, 123, 124],
    "jild28-nafha-5": [124, 125],
    "jild28-nafha-6": [125, 126, 127, 128, 129, 130, 131, 132],
    "jild28-nafha-7": [132, 133, 134],
    "jild28-nafha-8": [134, 135, 136],
    "jild28-nafha-9": [136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149],
    "jild28-nafha-10": [149, 150, 151, 152, 153, 154, 155],
    "jild28-shamama-3-nufha-1": [156, 157, 158, 159, 160, 161, 162, 163],
    "jild28-shamama-3-nufha-2": [163, 164, 165, 166, 167],
    "jild28-shamama-3-nufha-3": [167, 168, 169, 170, 171, 172, 173],
    "jild28-shamama-4-intro": [174, 175, 176],
    "jild28-shamama-4-nufha-1": [176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199],
    "jild28-shamama-4-nufha-2": [199, 200, 201, 202, 203, 204, 205, 206],
    "jild28-shamama-4-nufha-3": [206, 207, 208, 209, 210, 211, 212, 213, 214, 215],
    "jild28-shamama-4-nufha-4": [215, 216, 217, 218],
    "jild28-shamama-4-nufha-5": [218, 219],
    "jild28-shamama-4-nufha-6": [219, 220, 221, 222, 223, 224, 225],
    "jild28-shamama-4-nufha-7": [225, 226, 227, 228, 229],
    "jild28-shamama-4-nufha-8": [229, 230, 231, 232],
    "jild28-shamama-4-nufha-9": [232, 233, 234, 235, 236, 237, 238],
    "jild28-shamama-4-nufha-10": [238, 239, 240, 241, 242, 243, 244, 245, 246, 247],
    "jild28-shamama-4-nufha-11": [247, 248, 249],
    "jild28-shamama-4-nufha-12": [249, 250, 251],
    "jild28-shamama-4-nufha-13": [251, 252, 253, 254],
    "jild28-shamama-4-nufha-14": [254, 255, 256, 257, 258, 259, 260, 261],
    "jild28-shamama-4-nufha-15": [261, 262, 263, 264, 265, 266],
    "jild28-shamama-4-nufha-16": [266, 267, 268, 269, 270, 271],
    "jild28-shamama-4-nufha-17": [271, 272, 273],
    "jild28-shamama-4-nufha-18": [274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286],
    "jild28-shamama-4-nufha-19": [286, 287, 288, 289],
    "jild28-shamama-4-nufha-20": [289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303],
    "jild28-shamama-4-nufha-21": [303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334],
    "jild28-risala-535-tatimma": [336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 356, 357, 358, 359, 360],
    "jild28-masala-4": [361],
    "jild28-masala-5": [361, 362, 363, 365, 366],
    "jild28-masala-6-ta-10": [366, 367],
    "jild28-masala-11": [368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403],
    "jild28-masala-12": [404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414],
    "jild28-masala-13": [414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428],
    "jild28-masala-8": [428, 429, 430, 431],
    "jild28-deobandi-fatwa": [432, 433],
    "jild28-masala-19": [434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459],
    "jild28-masala-20": [459, 460, 461, 462, 463, 464, 465],
    "jild28-masala-21": [465, 466, 467, 468],
    "jild28-masala-22": [469, 470, 471, 472, 473, 474, 475, 476, 477, 478],
    "jild28-masala-22-doom": [478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489],
    "jild28-zulal-intro": [491, 493, 494, 495, 496, 497, 498, 499, 500, 501],
    "jild28-zulal-muqaddima-1": [501, 502, 503, 504, 505, 506],
    "jild28-zulal-muqaddima-2": [506, 507, 508, 509, 510, 511, 512, 513],
    "jild28-zulal-razi-dalil": [513, 514, 515, 516, 517, 518, 519, 520, 521, 522],
    "jild28-zulal-munaqasha-1": [522, 523, 524, 525, 526, 527],
    "jild28-zulal-munaqasha-2": [527, 528, 529, 530, 531],
    "jild28-zulal-shubha-1-muqaddimat": [531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550],
    "jild28-zalal-nqi-muqaddima-3": [550, 551, 552, 553, 554, 555, 556, 557],
    "jild28-zalal-nqi-muqaddima-4": [557, 558, 559, 560],
    "jild28-zalal-nqi-muqaddima-5": [560, 561],
    "jild28-zalal-nqi-talkhis": [561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578],
    "jild28-zalal-nqi-radd-abu-ubayda": [579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 595, 596, 597, 598, 599, 600, 601, 602, 603],
    "jild28-risala-77-shubha-2": [603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617],
    "jild28-risala-77-shubha-3": [617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640],
    "jild28-zulal-tadhyeel": [641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651],
    "jild28-zulal-takmeel": [651, 652, 653, 654],
    "jild28-zulal-tasjeel": [654, 655],
    "jild28-zulal-wajh-thani": [655, 656, 657, 658, 659, 660],
    "jild28-zulal-wajh-thalis": [660, 661, 662],
    "jild28-zulal-tanbih": [662, 663, 664, 665, 666, 667],
    "jild28-zulal-khatima": [668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681],
    "jild28-zulal-latifa-layl": [681, 682, 683],
    "jild28-zulal-latifa-baqillani": [683, 684, 685, 686],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 14, f"expected 14 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        # Jild 28 has no missing-notes quirk: every leaf item carries
        # a "notes" key (asserted here); nothing to normalise.
        for it in items:
            assert "notes" in it, f"{it['id']}: missing notes key"
        all_items.extend(items)

    # COMBINES (5): two-part merges, all parts empty sawal,
    # sawal stays empty, title from the FIRST part (== merged-v3
    # title), jawab = " ".join of the stripped part jawabs
    # (one space at the seam: every head ends with "۔" and every
    # tail starts with "یہ", no space either side), pages = sorted
    # union, notes = concatenation in order. RENAME-ONLY (16): the
    # plain nafha-N ids of chunks 05/06 (lesson 535) move to the
    # shamama-4-nufha-N form; chunk 03's plain nafha-1..10 (lesson
    # 533) keep their ids. Renames apply AFTER the combines.

    def combine_parts(result_id, selectors, seam_checks, expected_jawab_len):
        parts = []
        used = set()
        for sel_id, sel_start in selectors:
            hits = [it for it in all_items
                    if it["id"] == sel_id
                    and (sel_start is None or it.get("start_page") == sel_start)
                    and id(it) not in used]
            assert hits, f"{result_id}: no part matched ({sel_id}, {sel_start})"
            for it in hits:
                used.add(id(it))
            parts.extend(hits)
        parts.sort(key=lambda it: min(it["pages"]))
        assert [min(p["pages"]) for p in parts] == sorted(min(p["pages"]) for p in parts), (
            f"{result_id}: parts not in page order"
        )
        vols = {p.get("volume_id") for p in parts}
        assert vols == EXPECTED_VOLUME_IDS, f"{result_id}: volume mismatch {vols}"
        assert all(not p.get("tashreeh_sawal") for p in parts), (
            f"{result_id}: a part sawal is non-empty"
        )
        for part_no, which, needle in seam_checks:
            txt = parts[part_no].get("tashreeh_jawab") or ""
            if which == "end":
                assert txt.rstrip().endswith(needle), (
                    f"{result_id} part {part_no + 1} end seam mismatch: ...{txt.rstrip()[-60:]!r}"
                )
            else:
                assert txt.lstrip().startswith(needle), (
                    f"{result_id} part {part_no + 1} start seam mismatch: {txt.lstrip()[:60]!r}"
                )
        title = parts[0]["title"]
        assert title == V3_TITLES[result_id], f"{result_id}: first-part title != v3 title"
        pages = sorted({p for part in parts for p in part["pages"]})
        assert pages == V3_PAGES[result_id], f"{result_id}: combined pages != v3"
        joined = {
            "id": result_id,
            "title": title,
            "volume_id": parts[0]["volume_id"],
            "pages": pages,
            "start_page": min(pages),
            "tashreeh_sawal": "",
            "tashreeh_jawab": " ".join(p["tashreeh_jawab"].strip() for p in parts if p.get("tashreeh_jawab")),
            "notes": [n for p in parts for n in p.get("notes", [])],
        }
        assert len(joined["tashreeh_jawab"]) == expected_jawab_len, (
            f"{result_id}: joined jawab {len(joined['tashreeh_jawab'])} chars != expected {expected_jawab_len}"
        )
        assert joined["tashreeh_jawab"], f"{result_id}: combined jawab is empty"
        idxs = [i for i, it in enumerate(all_items) if any(it is p for p in parts)]
        assert len(idxs) == len(parts), f"{result_id}: part index mismatch"
        first = idxs[0]
        for i in reversed(idxs[1:]):
            del all_items[i]
        all_items[first] = joined
        print(f"combined {result_id}: {len(parts)} parts -> 1 item, {len(pages)} pages, jawab {expected_jawab_len} chars, notes {len(joined['notes'])}")

    V3_TITLES = {
        "jild28-shamama-4-nufha-3": "الشمامۃ الرابعۃ — نفحہ ۳: عند حضور کے لیے ہے (جاری)",
        "jild28-shamama-4-nufha-14": "نفحہ ۱۴ — علماء کے سکوت و انکار کی وجہ اور مجددین کا طریقہ (جاری)",
        "jild28-shamama-4-nufha-21": "نفحہ ۲۱ (آغاز) — قہستانی کی شرحِ نقایہ",
        "jild28-zulal-shubha-1-muqaddimat": "پہلا شبہ — «اتقی» کی تفسیر تقی سے اور اس کے جواب کے مقدمات",
        "jild28-zalal-nqi-radd-abu-ubayda": "الزلال النقی — ابو عبیدہ کے رد کی تکمیل: ابو طالب، تین وجوہ اور استخدام",
        "jild28-shamama-4-nufha-4": "نفحہ ۴ — «عند» کا ترجمہ نزد و پاس اور منبر چوری کی صورت",
        "jild28-shamama-4-nufha-5": "نفحہ ۵ — «عند» ظرف زمان و مکان بھی ہے",
        "jild28-shamama-4-nufha-6": "نفحہ ۶ — «علی المنبر» سے استدلال کا رد: «علی» کے حقیقی معنی لزوم و مصاحبت و زمان",
        "jild28-shamama-4-nufha-7": "نفحہ ۷ — چھ وجوہ سے اذان «علی المنبر» سے استدلال باطل",
        "jild28-shamama-4-nufha-8": "نفحہ ۸ — ائمہ مالکیہ کے نزدیک اذان خطبہ منارہ پر سنت ہے",
        "jild28-shamama-4-nufha-9": "نفحہ ۹ — تعامل کا دعویٰ باطل ہے",
        "jild28-shamama-4-nufha-10": "نفحہ ۱۰ — توارث کی تحقیق: چار حالتیں اور ثانوی کے دعوے کا رد",
        "jild28-shamama-4-nufha-11": "نفحہ ۱۱ — توارث کے مدعیوں سے مطالبہ دلیل اور ان کی عقلی دلیل کا رد",
        "jild28-shamama-4-nufha-12": "نفحہ ۱۲ — توارث البعض حدیث کے خلاف حجت نہیں: اذان فجر کی مثال",
        "jild28-shamama-4-nufha-13": "نفحہ ۱۳ — مؤذن حرمین کے فعل سے استدلال کا رد",
        "jild28-shamama-4-nufha-15": "نفحہ ۱۵ — جویبر کا اثر اور اس کا رد",
        "jild28-shamama-4-nufha-16": "نفحہ ۱۶ — طلق بن علی، ابن عمر اور ابو ہریرہ کے آثار",
        "jild28-shamama-4-nufha-17": "نفحہ ۱۷ — ابن ماجہ کی حدیثِ عبداللہ بن زید",
        "jild28-shamama-4-nufha-18": "نفحہ ۱۸ — آیتِ حج سے استدلال اور مقامِ ابراہیم",
        "jild28-shamama-4-nufha-19": "نفحہ ۱۹ — آیاتِ ذکر سے استدلال",
        "jild28-shamama-4-nufha-20": "نفحہ ۲۰ — امام مالک کا قول اور ملا علی قاری کی تطبیق",
    }

    combine_parts(
        "jild28-shamama-4-nufha-3",
        [('jild28-shamama-4-nufha-3', None), ('jild28-nafha-3', 213)],
        [
            (0, "end", "لحاظ سے سامنے ہونا۔ یہ نفحہ یہیں ختم نہیں ہوتا، اس کا بقیہ اگلے حصے میں جاری ہے۔"),
            (1, "start", "یہ حصہ اسی بحث کا باقی حصہ ہے جس میں لفظ «عند» کے معنی سمجھائے جا رہے ہیں۔ اعلیٰ"),
        ],
        9069,
    )
    combine_parts(
        "jild28-shamama-4-nufha-14",
        [('jild28-nafha-14', None)],
        [
            (0, "end", "ا، نحیف کا مطلب ہے دبلا پتلا، رنگ بریدہ کا مطلب ہے جس کے چہرے کا رنگ اڑا ہوا ہو۔"),
            (1, "start", "یہ حصہ غوثِ اعظم رحمۃ اللہ علیہ کے اس واقعے کی تکمیل ہے — تکمیل کا مطلب ہے کہ وا"),
        ],
        10367,
    )
    combine_parts(
        "jild28-shamama-4-nufha-21",
        [('jild28-nafha-21', None), ('jild28-risala-535', None)],
        [
            (0, "end", "ے اس میں وہ صورت بھی شامل ہے جو ان دو جہتوں سے باہر ہو، اس کا بیان آگے آ رہا ہے۔"),
            (1, "start", "یہ حصہ چوتھے شمامے کے اس موڑ سے شروع ہوتا ہے جہاں علامہ قہستانی کی ایک عبارت زیر"),
        ],
        36882,
    )
    combine_parts(
        "jild28-zulal-shubha-1-muqaddimat",
        [('jild28-zulal-shubha-1-muqaddimat', None), ('jild28-zalal-nqi-1', None)],
        [
            (0, "end", "نا، مرغوب کا مطلب ہے پسندیدہ، اور دور از کار کا مطلب ہے کام سے دور، یعنی بے کار۔"),
            (1, "start", "یہ بات پچھلے صفحے سے چل رہی ہے۔ کچھ لوگوں کو ایسی باتیں گھڑنے کی لت لگ جاتی ہے ج"),
        ],
        26633,
    )
    combine_parts(
        "jild28-zalal-nqi-radd-abu-ubayda",
        [('jild28-zalal-nqi-radd-abu-ubayda', None), ('jild28-risala-77-shubha-1', None)],
        [
            (0, "end", "سمجھداری — پھر اس کے دو جواب دیے: پہلا تو وہی جو علماء نے اختیار فرمایا، یعنی..."),
            (1, "start", "یہ شبہۂ اولٰی کے جواب کا بقیہ حصہ ہے، جو پچھلے حصے سے چلا آ رہا ہے۔ اعلیٰ حضرت "),
        ],
        28623,
    )
    print(f"after joins: {len(all_items)} items (94 concatenated)")
    # RENAME-ONLY (16): plain nafha-N ids of chunks 05/06 (lesson 535)
    # move to the shamama-4-nufha-N form; chunk 03's plain nafha-1..10
    # (lesson 533) keep their ids. Scoped by start_page.
    for old_id, start_page, new_id in [
        ("jild28-nafha-4", 215, "jild28-shamama-4-nufha-4"),
        ("jild28-nafha-5", 218, "jild28-shamama-4-nufha-5"),
        ("jild28-nafha-6", 219, "jild28-shamama-4-nufha-6"),
        ("jild28-nafha-7", 225, "jild28-shamama-4-nufha-7"),
        ("jild28-nafha-8", 229, "jild28-shamama-4-nufha-8"),
        ("jild28-nafha-9", 232, "jild28-shamama-4-nufha-9"),
        ("jild28-nafha-10", 238, "jild28-shamama-4-nufha-10"),
        ("jild28-nafha-11", 247, "jild28-shamama-4-nufha-11"),
        ("jild28-nafha-12", 249, "jild28-shamama-4-nufha-12"),
        ("jild28-nafha-13", 251, "jild28-shamama-4-nufha-13"),
        ("jild28-nafha-15", 261, "jild28-shamama-4-nufha-15"),
        ("jild28-nafha-16", 266, "jild28-shamama-4-nufha-16"),
        ("jild28-nafha-17", 271, "jild28-shamama-4-nufha-17"),
        ("jild28-nafha-18", 274, "jild28-shamama-4-nufha-18"),
        ("jild28-nafha-19", 286, "jild28-shamama-4-nufha-19"),
        ("jild28-nafha-20", 289, "jild28-shamama-4-nufha-20"),
    ]:
        assert not any(it["id"] == new_id for it in all_items), (
            f"rename target {new_id} already exists"
        )
        hits = [it for it in all_items
                if it["id"] == old_id and it.get("start_page") == start_page]
        assert len(hits) == 1, (
            f"rename source {old_id} @ {start_page}: expected 1 item, found {len(hits)}"
        )
        assert hits[0]["pages"] == V3_PAGES[new_id], f"{new_id}: pages != v3"
        assert hits[0]["title"] == V3_TITLES[new_id], f"{new_id}: title != v3"
        hits[0]["id"] = new_id
        print(f"renamed {old_id} @ {start_page} -> {new_id}")
    print("renames applied: 16")
    # The duplicate-id assertion runs AFTER the renames, not after
    # the combines: nafha-4..10 are duplicated across chunks 03 and
    # 05 until the renames disambiguate them (lesson of the first
    # J28 dry-run).
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS after renames: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print(f"after renames: {len(all_items)} items, all ids unique")
    # Absorbed ids must be gone (chunk 05's nafha-3 is checked
    # start_page-scoped: chunk 03's nafha-3 keeps the plain id).
    assert not any(it["id"] == "jild28-nafha-14" for it in all_items), f"absorbed id jild28-nafha-14 still present"
    assert not any(it["id"] == "jild28-nafha-21" for it in all_items), f"absorbed id jild28-nafha-21 still present"
    assert not any(it["id"] == "jild28-risala-535" for it in all_items), f"absorbed id jild28-risala-535 still present"
    assert not any(it["id"] == "jild28-zalal-nqi-1" for it in all_items), f"absorbed id jild28-zalal-nqi-1 still present"
    assert not any(it["id"] == "jild28-risala-77-shubha-1" for it in all_items), f"absorbed id jild28-risala-77-shubha-1 still present"
    assert not any(it["id"] == "jild28-nafha-3" and it.get("start_page") == 213 for it in all_items), "chunk-05 nafha-3 still present"
    # STABLE SORT by start_page, mirroring the v3 merge.
    all_items.sort(key=lambda it: it["start_page"])
    print(f"sorted by start_page: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    assert total_markers == 0, f"page markers remain in output: {total_markers}"
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-28.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-28.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
