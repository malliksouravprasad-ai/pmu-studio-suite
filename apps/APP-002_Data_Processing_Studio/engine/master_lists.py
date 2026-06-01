"""Built-in master lists for APP-004 Lookup & Mapping Engine."""

# ── Odisha Districts (canonical spellings) ─────────────────────────────────
ODISHA_DISTRICTS = [
    "Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh",
    "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam",
    "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal",
    "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri",
    "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri",
    "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh",
]

# Lowercase alias → canonical spelling
DISTRICT_VARIANTS: dict = {
    # Kendujhar variants
    "keonjhar": "Kendujhar", "kenjhar": "Kendujhar", "kendujhor": "Kendujhar",
    "kendujhar dist": "Kendujhar", "keonjhar dist": "Kendujhar",
    "keonjhar district": "Kendujhar",

    # Khordha variants
    "khurda": "Khordha", "khurdha": "Khordha", "khorda": "Khordha",
    "khurda dist": "Khordha", "khurda district": "Khordha",

    # Subarnapur / Sonepur variants
    "sonepur": "Subarnapur", "sonapur": "Subarnapur", "subarnapur": "Subarnapur",
    "sonepur dist": "Subarnapur", "subarnapur dist": "Subarnapur",

    # Balasore variants
    "baleswar": "Balasore", "baleswara": "Balasore", "baleshwar": "Balasore",
    "baleswar dist": "Balasore", "baleswar district": "Balasore",
    "balashwar": "Balasore",

    # Sundargarh variants
    "sundergarh": "Sundargarh", "sundargar": "Sundargarh",
    "sundergarh dist": "Sundargarh", "sundergarh district": "Sundargarh",

    # Boudh variants
    "baudh": "Boudh", "baudh dist": "Boudh",

    # Balangir variants
    "bolangir": "Balangir", "bolangir dist": "Balangir",
    "balangir dist": "Balangir",

    # Kandhamal variants
    "phulbani": "Kandhamal", "kandhamal dist": "Kandhamal",

    # Jagatsinghpur variants
    "jagatsinhpur": "Jagatsinghpur", "jagatsingpur": "Jagatsinghpur",

    # Deogarh variants
    "deogar": "Deogarh", "devgarh": "Deogarh",

    # Kalahandi variants
    "kalahandi dist": "Kalahandi",

    # Other common abbreviations
    "cuttack dist": "Cuttack", "puri dist": "Puri", "ganjam dist": "Ganjam",
    "angul dist": "Angul", "jajpur dist": "Jajpur",
    "mayurbhanj dist": "Mayurbhanj", "koraput dist": "Koraput",
    "gajapati dist": "Gajapati", "bargarh dist": "Bargarh",
    "nuapada dist": "Nuapada", "nayagarh dist": "Nayagarh",
    "rayagada dist": "Rayagada", "sambalpur dist": "Sambalpur",
    "nabarangpur dist": "Nabarangpur", "malkangiri dist": "Malkangiri",
    "kendrapara dist": "Kendrapara", "jharsuguda dist": "Jharsuguda",
    "dhenkanal dist": "Dhenkanal", "bhadrak dist": "Bhadrak",
}

# ── Odisha Blocks (canonical, selected key districts) ─────────────────────
ODISHA_BLOCKS = [
    # Cuttack
    "Athagarh","Athamallik","Banki","Baramba","Cuttack Sadar","Dampara","Jagatpur",
    "Kantapada","Mahanga","Narasinghpur","Niali","Nimapada","Salepur","Tangi-Choudwar",
    # Puri
    "Astarang","Brahmagiri","Delanga","Gop","Kakatpur","Kanas","Konark","Krushnaprasad",
    "Nimapada","Pipli","Puri Sadar","Satyabadi","Sijua",
    # Khordha
    "Balipatna","Balianta","Begunia","Bolagarh","Chilika","Jatni","Khordha",
    "Ranpur","Tangi",
    # Ganjam
    "Aska","Beguniapada","Berhampur","Bhanjanagar","Buguda","Chhatrapur",
    "Dharakote","Digapahandi","Gobindapur","Hinjilicut","Kabisuryanagar",
    "Kukudakhandi","Patrapur","Polasara","Purushottampur","R.Udayagiri",
    "Rangeilunda","Sanakhemundi","Sheragada","Surada",
    # Kendujhar
    "Anandapur","Banspal","Barbil","Champua","Ghasipura","Harichandanpur",
    "Joda","Jujumura","Kendujhar","Keonjhar","Telkoi","Turumunga",
    # Sambalpur
    "Jamankira","Kuchinda","Maneswar","Naktideul","Rairakhol",
    "Sambalpur Sadar",
    # Balasore
    "Balasore Sadar","Bahanaga","Basta","Bhograi","Jaleswar","Khaira",
    "Nilgiri","Oupada","Remuna","Simulia","Soro",
    # Mayurbhanj
    "Badasahi","Badampahar","Bangriposi","Baripada","Betnoti","Bijatala",
    "Bisoi","Jashipur","Joshipur","Karanjia","Khunta","Kuliana",
    "Morada","Raruan","Rairangpur","Saraskana","Shamakhunta","Suliapada",
    "Tato","Thakurmunda","Udala",
]

BLOCK_VARIANTS: dict = {
    "sadar": None,  # ambiguous — needs district context
    "cuttack sadar": "Cuttack Sadar",
    "puri sadar": "Puri Sadar",
    "balasore sadar": "Balasore Sadar",
    "keonjhar": "Kendujhar",
    "keonjhar sadar": "Keonjhar",
}

# ── Yes/No normalization ────────────────────────────────────────────────────
YES_NO_LIST   = ["Yes", "No"]
YES_VARIANTS  = {"yes", "y", "1", "true", "ya", "han", "haan"}
NO_VARIANTS   = {"no",  "n", "0", "false", "na", "nahi", "nhi"}
YES_NO_VARIANTS: dict = {
    **{v: "Yes" for v in YES_VARIANTS},
    **{v: "No"  for v in NO_VARIANTS},
}


def get_master_list(mapping_type: str) -> tuple:
    """Return (master_list, variant_map) for a given mapping type."""
    if mapping_type == "district":
        return ODISHA_DISTRICTS, DISTRICT_VARIANTS
    if mapping_type == "block":
        return ODISHA_BLOCKS, BLOCK_VARIANTS
    if mapping_type == "yesno":
        return YES_NO_LIST, YES_NO_VARIANTS
    return [], {}
