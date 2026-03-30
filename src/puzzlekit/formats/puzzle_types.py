from typing import Dict, List, Optional, Set

# Single source of truth: canonical IR type -> per-format metadata.
# key: Intermediate Representation (IR) puzzle type.
# value:
# - puzzlink.aliases: accepted source names / aliases
# - puzzlink.primary: preferred type token when encoding puzz.link URL
# - puzzlink.family: decode/encode pipeline family in PuzzlinkConverter
# - penpa.aliases: accepted genre-tag aliases when decoding penpa
# - penpa.genre_tag: preferred genre tag when encoding penpa
# If penpa.genre_tag is omitted, a placeholder (canonical type) is used.

PUZZLE_TYPES_DICT: Dict[str, Dict[str, Dict[str, object]]] = {
    "heyawake": {
        "puzzlink": {"aliases": ["heyawake", "heyawacky", "heyawack"], "primary": "heyawake", "family": "heyawake_family"},
        "penpa": {"aliases": ["heyawake"], "genre_tag": "heyawake"},
    },
    "shikaku": {
        "puzzlink": { "aliases": ["shikaku"], "primary": "shikaku", "family": "heyawake_family"},
        "penpa": { "aliases": ["shikaku"], 'genre_tag': ['shikaku']},
    },
    "aqre": {
        "puzzlink": {"aliases": ["aqre"], "primary": "aqre", "family": "heyawake_family"},
        "penpa": {"aliases": ["aqre"], "genre_tag": "aqre"},
    },
    "shimaguni": {
        "puzzlink": {"aliases": ["shimaguni"], "primary": "shimaguni", "family": "heyawake_family"},
        "penpa": {"aliases": ["shimaguni (islands)"], "genre_tag": "shimaguni (islands)"},
    },
    "stostone": {
        "puzzlink": {"aliases": ["stostone"], "primary": "stostone", "family": "heyawake_family"},
        "penpa": {"aliases": ["stostone"]},
    },
    "ayeheya": {
        "puzzlink": {"aliases": ["ayeheya"], "primary": "ayeheya", "family": "heyawake_family"},
        "penpa": {"aliases": ["ayeheya (ekawayeh)"], "genre_tag": "ayeheya (ekawayeh)"},
    },
    "country": {
        "puzzlink": {"aliases": ["country"], "primary": "country", "family": "heyawake_family"},
        "penpa": {"aliases": ["country road"], "genre_tag": "country road"},
    },
    "nonogram": {
        "puzzlink": {"aliases": ["nonogram"], "primary": "nonogram", "family": "nonogram_family"},
        "penpa": {"aliases": ["nonogram"]},
    },
    "nurikabe": {
        "puzzlink": {"aliases": ["nurikabe"], "primary": "nurikabe", "family": "nurikabe_family"},
        "penpa": {"aliases": ["nurikabe"]},
    },
    "kurochute": {
        "puzzlink": {"aliases": ["kurochute", "kuroshuto", "kurochuto"], "primary": "kurochute", "family": "nurikabe_family"},
        "penpa": {"aliases": ["kurochute"], "genre_tag": "kurochute"},
    },
    "kurodoko": {
        "puzzlink": {"aliases": ["kurodoko"], "primary": "kurodoko", "family": "nurikabe_family"},
        "penpa": {"aliases": ["kurodoko"]},
    },
    "kurotto": {
        "puzzlink": {"aliases": ["kurotto"], "primary": "kurotto", "family": "nurikabe_family"},
        "penpa": {"aliases": ["kurotto"]},
    },
    "nurimisaki": {
        "puzzlink": {"aliases": ["nurimisaki"], "primary": "nurimisaki", "family": "nurikabe_family"},
        "penpa": {"aliases": ["nurimisaki"]},
    },
    "moonsun": {
        "puzzlink": {"aliases": ["moonsun"], "primary": "moonsun", "family": "masyu_family"},
        "penpa": {"aliases": ["moonsun"], 'genre_tag': 'moon or sun'},
    },
    "masyu": {
        "puzzlink": {"aliases": ["masyu", "mashu", "pearl"], "primary": "masyu", "family": "masyu_family"},
        "penpa": {"aliases": ["masyu"]},
    },
    "slitherlink": {
        "puzzlink": {"aliases": ["slitherlink", "slither", "vslither", "tslither"], "primary": "slither", "family": "slither_family"},
        "penpa": {"aliases": ["slitherlink"], "genre_tag": "slitherlink"},
    },
    "yajilin": {
        "puzzlink": {"aliases": ["yajilin", "yajirin"], "primary": "yajilin", "family": "yajilin_family"},
        "penpa": {"aliases": ["yajilin"], "genre_tag": "yajilin"},
    },
    "castle": {
        "puzzlink": {"aliases": ["castle"], "primary": "castle", "family": "yajilin_family"},
        "penpa": {"aliases": ["castlewall"], "genre_tag": "castlewall"},
    },
    "hebi": {
        "puzzlink": {"aliases": ["hebi", "snakes"], "primary": "hebi", "family": "yajilin_family"},
        "penpa": {"aliases": ["hebi-ichigo"], "genre_tag": "hebi-ichigo"},
    }
}


def _invert_family_groups(groups: Dict[str, Set[str]]) -> Dict[str, str]:
    """Build canonical_type -> family map with collision guard."""
    inverted: Dict[str, str] = {}
    for family, type_set in groups.items():
        for puzzle_type in type_set:
            if puzzle_type in inverted and inverted[puzzle_type] != family:
                raise ValueError(f"Puzzle type '{puzzle_type}' mapped to multiple families.")
            inverted[puzzle_type] = family
    return inverted


# Canonical puzzle types used in IR.
IR_PUZZLE_TYPES: Set[str] = set(PUZZLE_TYPES_DICT.keys())

# External/source aliases -> canonical IR puzzle type.
PUZZLE_TYPE_ALIASES: Dict[str, str] = {}
for canonical, meta in PUZZLE_TYPES_DICT.items():
    PUZZLE_TYPE_ALIASES[canonical] = canonical
    for alias in meta.get("puzzlink", {}).get("aliases", []):
        PUZZLE_TYPE_ALIASES[str(alias).strip().lower()] = canonical
    for alias in meta.get("penpa", {}).get("aliases", []):
        PUZZLE_TYPE_ALIASES[str(alias).strip().lower()] = canonical

# Canonical -> primary puzz.link type token for encoding URLs.
IR_TO_PUZZLINK_TYPE: Dict[str, str] = {
    canonical: str(meta.get("puzzlink", {}).get("primary", canonical))
    for canonical, meta in PUZZLE_TYPES_DICT.items()
}

# Puzzlink pipeline groups (family -> canonical type set), auto-generated.
PUZZLINK_FAMILY_GROUPS: Dict[str, Set[str]] = {}
for canonical, meta in PUZZLE_TYPES_DICT.items():
    family = meta.get("puzzlink", {}).get("family")
    if family:
        fam = str(family)
        PUZZLINK_FAMILY_GROUPS.setdefault(fam, set()).add(canonical)

# Keep decode/encode group names for compatibility and future divergence.
PUZZLINK_DECODE_FAMILY_GROUPS: Dict[str, Set[str]] = {
    family: set(types) for family, types in PUZZLINK_FAMILY_GROUPS.items()
}
PUZZLINK_ENCODE_FAMILY_GROUPS: Dict[str, Set[str]] = {
    family: set(types) for family, types in PUZZLINK_FAMILY_GROUPS.items()
}

# Canonical IR type -> family (auto-generated from groups).
PUZZLINK_DECODE_FAMILY: Dict[str, str] = _invert_family_groups(PUZZLINK_DECODE_FAMILY_GROUPS)
PUZZLINK_ENCODE_FAMILY: Dict[str, str] = _invert_family_groups(PUZZLINK_ENCODE_FAMILY_GROUPS)

# Canonical types currently supported by PuzzlinkConverter.encode().
PUZZLINK_ENCODABLE_TYPES: Set[str] = set(PUZZLINK_ENCODE_FAMILY.keys())


def normalize_puzzle_type(puzzle_type: str) -> str:
    """Normalize an external puzzle type into canonical IR type."""
    key = (puzzle_type or "").strip().lower()
    return PUZZLE_TYPE_ALIASES.get(key, key)


def to_puzzlink_type(canonical_type: str) -> str:
    """Map canonical IR type to a puzz.link type token."""
    return IR_TO_PUZZLINK_TYPE.get(canonical_type, canonical_type)


def get_penpa_genre_tags(canonical_type: str) -> List[str]:
    """
    Return penpa genre tags for encoding.

    If genre_tag is not explicitly provided, use canonical type as placeholder.
    """
    norm = normalize_puzzle_type(canonical_type)
    meta = PUZZLE_TYPES_DICT.get(norm, {})
    penpa_meta = meta.get("penpa", {})
    genre_tag = str(penpa_meta.get("genre_tag", norm))
    return [genre_tag]


def get_puzzlink_decode_family(canonical_type: str) -> Optional[str]:
    return PUZZLINK_DECODE_FAMILY.get(canonical_type)


def get_puzzlink_encode_family(canonical_type: str) -> Optional[str]:
    return PUZZLINK_ENCODE_FAMILY.get(canonical_type)