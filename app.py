import re

import pandas as pd
import streamlit as st

# Popular fragrances not in store inventory — profile used to match in-store stock
EXTERNAL_FRAGRANCES = {
    "sauvage": {
        "name": "Sauvage",
        "brand": "Dior",
        "family": "Aromatic Fougère",
        "notes": "Bergamot, Pepper, Ambroxan, Lavender, Patchouli",
    },
    "dior sauvage": {
        "name": "Sauvage",
        "brand": "Dior",
        "family": "Aromatic Fougère",
        "notes": "Bergamot, Pepper, Ambroxan, Lavender, Patchouli",
    },
    "eros": {
        "name": "Eros",
        "brand": "Versace",
        "family": "Amber Aromatic",
        "notes": "Mint, Green Apple, Lemon, Tonka Bean, Vanilla, Cedar",
    },
    "versace eros": {
        "name": "Eros",
        "brand": "Versace",
        "family": "Amber Aromatic",
        "notes": "Mint, Green Apple, Lemon, Tonka Bean, Vanilla, Cedar",
    },
    "bleu de chanel": {
        "name": "Bleu de Chanel",
        "brand": "Chanel",
        "family": "Woody Aromatic",
        "notes": "Grapefruit, Mint, Pink Pepper, Ginger, Cedar, Sandalwood",
    },
    "acqua di gio": {
        "name": "Acqua di Giò",
        "brand": "Giorgio Armani",
        "family": "Aromatic Aquatic",
        "notes": "Marine Notes, Bergamot, Neroli, Rosemary, Patchouli, Musk",
    },
    "light blue": {
        "name": "Light Blue",
        "brand": "Dolce & Gabbana",
        "family": "Citrus Aromatic",
        "notes": "Sicilian Lemon, Apple, Bamboo, Cedar, Amber, Musk",
    },
    "dolce light blue": {
        "name": "Light Blue",
        "brand": "Dolce & Gabbana",
        "family": "Citrus Aromatic",
        "notes": "Sicilian Lemon, Apple, Bamboo, Cedar, Amber, Musk",
    },
    "black opium": {
        "name": "Black Opium",
        "brand": "Yves Saint Laurent",
        "family": "Oriental Vanilla",
        "notes": "Pear, Pink Pepper, Coffee, Jasmine, Vanilla, Patchouli",
    },
    "good girl": {
        "name": "Good Girl",
        "brand": "Carolina Herrera",
        "family": "Floral Gourmand",
        "notes": "Almond, Coffee, Jasmine, Tuberose, Tonka Bean, Cacao",
    },
    "carolina herrera good girl": {
        "name": "Good Girl",
        "brand": "Carolina Herrera",
        "family": "Floral Gourmand",
        "notes": "Almond, Coffee, Jasmine, Tuberose, Tonka Bean, Cacao",
    },
    "libre": {
        "name": "Libre",
        "brand": "Yves Saint Laurent",
        "family": "Floral",
        "notes": "Lavender, Mandarin, Orange Blossom, Jasmine, Vanilla, Amber",
    },
    "ysl libre": {
        "name": "Libre",
        "brand": "Yves Saint Laurent",
        "family": "Floral",
        "notes": "Lavender, Mandarin, Orange Blossom, Jasmine, Vanilla, Amber",
    },
    "lost cherry": {
        "name": "Lost Cherry",
        "brand": "Tom Ford",
        "family": "Floral Gourmand",
        "notes": "Black Cherry, Cherry Liqueur, Almond, Rose, Tonka Bean, Vanilla",
    },
    "tom ford lost cherry": {
        "name": "Lost Cherry",
        "brand": "Tom Ford",
        "family": "Floral Gourmand",
        "notes": "Black Cherry, Cherry Liqueur, Almond, Rose, Tonka Bean, Vanilla",
    },
    "baccarat rouge 540": {
        "name": "Baccarat Rouge 540",
        "brand": "Maison Francis Kurkdjian",
        "family": "Amber Floral",
        "notes": "Saffron, Jasmine, Amberwood, Ambergris, Cedar, Fir Resin",
    },
    "creed aventus": {
        "name": "Aventus",
        "brand": "Creed",
        "family": "Woody Fruity",
        "notes": "Pineapple, Bergamot, Birch, Patchouli, Musk, Oakmoss, Vanilla",
    },
    "1 million": {
        "name": "1 Million",
        "brand": "Paco Rabanne",
        "family": "Woody Spicy",
        "notes": "Grapefruit, Mint, Cinnamon, Rose, Amber, Leather, Patchouli",
    },
    "paco rabanne 1 million": {
        "name": "1 Million",
        "brand": "Paco Rabanne",
        "family": "Woody Spicy",
        "notes": "Grapefruit, Mint, Cinnamon, Rose, Amber, Leather, Patchouli",
    },
    "angel": {
        "name": "Angel",
        "brand": "Mugler",
        "family": "Amber Gourmand",
        "notes": "Cotton Candy, Coconut, Honey, Red Berries, Patchouli, Vanilla",
    },
    "thierry mugler angel": {
        "name": "Angel",
        "brand": "Mugler",
        "family": "Amber Gourmand",
        "notes": "Cotton Candy, Coconut, Honey, Red Berries, Patchouli, Vanilla",
    },
    "la vie est belle": {
        "name": "La Vie Est Belle",
        "brand": "Lancôme",
        "family": "Floral Fruity Gourmand",
        "notes": "Black Currant, Pear, Iris, Jasmine, Orange Blossom, Patchouli, Vanilla",
    },
    "flowerbomb": {
        "name": "Flowerbomb",
        "brand": "Viktor & Rolf",
        "family": "Floral",
        "notes": "Tea, Bergamot, Orchid, Rose, Jasmine, Patchouli, Musk",
    },
    "viktor rolf flowerbomb": {
        "name": "Flowerbomb",
        "brand": "Viktor & Rolf",
        "family": "Floral",
        "notes": "Tea, Bergamot, Orchid, Rose, Jasmine, Patchouli, Musk",
    },
    "chanel no 5": {
        "name": "No. 5",
        "brand": "Chanel",
        "family": "Floral Aldehyde",
        "notes": "Aldehydes, Neroli, Ylang-Ylang, Jasmine, Rose, Sandalwood, Vanilla",
    },
    "no. 5": {
        "name": "No. 5",
        "brand": "Chanel",
        "family": "Floral Aldehyde",
        "notes": "Aldehydes, Neroli, Ylang-Ylang, Jasmine, Rose, Sandalwood, Vanilla",
    },
    "miss dior": {
        "name": "Miss Dior",
        "brand": "Dior",
        "family": "Floral Chypre",
        "notes": "Blood Orange, Rose, Jasmine, Patchouli, Musk",
    },
    "jo malone wood sage": {
        "name": "Wood Sage & Sea Salt",
        "brand": "Jo Malone",
        "family": "Woody Aromatic",
        "notes": "Ambrette, Sea Salt, Sage, Grapefruit, Red Algae",
    },
    "tom ford oud wood": {
        "name": "Oud Wood",
        "brand": "Tom Ford",
        "family": "Woody Spicy",
        "notes": "Oud, Rosewood, Cardamom, Sandalwood, Vetiver, Tonka Bean",
    },
    "by the fireplace": {
        "name": "By the Fireplace",
        "brand": "Maison Martin Margiela",
        "family": "Woody Spicy",
        "notes": "Clove, Chestnut, Vanilla, Guaiac Wood, Cashmeran",
    },
    "le male": {
        "name": "Le Male",
        "brand": "Jean Paul Gaultier",
        "family": "Aromatic Fougère",
        "notes": "Mint, Lavender, Bergamot, Cinnamon, Vanilla, Tonka Bean",
    },
    "jean paul gaultier le male": {
        "name": "Le Male",
        "brand": "Jean Paul Gaultier",
        "family": "Aromatic Fougère",
        "notes": "Mint, Lavender, Bergamot, Cinnamon, Vanilla, Tonka Bean",
    },
}

FAMILY_KEYWORDS = [
    "Woody",
    "Floral",
    "Citrus",
    "Amber",
    "Aromatic",
    "Leather",
    "Aquatic",
    "Oriental",
    "Gourmand",
    "Spicy",
    "Musk",
    "Chypre",
    "Fougère",
]


@st.cache_data
def load_inventory() -> pd.DataFrame:
    df = pd.read_csv("inventory.csv")
    df.columns = df.columns.str.strip().str.lower()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip().str.lower()
    return df


def title_case(text: str) -> str:
    if not text or text == "nan":
        return ""
    return text.title()


def get_available_families(df: pd.DataFrame) -> list[str]:
    all_families = " ".join(df["primary olfactory family"].dropna().unique())
    available = []
    for keyword in FAMILY_KEYWORDS:
        if keyword.lower() in all_families.lower():
            available.append(keyword)
    return available


def find_in_inventory(df: pd.DataFrame, query: str) -> pd.Series | None:
    query = query.strip().lower()
    if not query:
        return None

    names = df["fragrance name"]
    pattern = rf"(?<![a-z0-9]){re.escape(query)}(?![a-z0-9])"
    boundary_matches = df[names.str.contains(pattern, case=False, na=False, regex=True)]

    if len(boundary_matches) == 1:
        return boundary_matches.iloc[0]
    if len(boundary_matches) > 1:
        return boundary_matches.iloc[0]

    substring_matches = df[names.str.contains(re.escape(query), case=False, na=False, regex=True)]
    if len(substring_matches) >= 1:
        return substring_matches.iloc[0]

    return None


def resolve_family_keyword(family: str) -> str:
    family = family.strip().lower()
    for keyword in FAMILY_KEYWORDS:
        if keyword.lower() in family:
            return keyword.lower()
    return family.split()[0] if family else ""


def lookup_external_fragrance(query: str) -> dict | None:
    query = query.strip().lower()
    if not query:
        return None

    if query in EXTERNAL_FRAGRANCES:
        return {**EXTERNAL_FRAGRANCES[query], "matched_as": query}

    best_match = None
    best_len = 0
    for name, profile in EXTERNAL_FRAGRANCES.items():
        if name in query or query in name:
            if len(name) > best_len:
                best_match = name
                best_len = len(name)

    if best_match:
        return {**EXTERNAL_FRAGRANCES[best_match], "matched_as": best_match}

    return None


def filter_by_family(df: pd.DataFrame, family: str) -> pd.DataFrame:
    family = family.strip().lower()
    mask = df["primary olfactory family"].str.contains(family, case=False, na=False)
    return df[mask].copy()


FAMILY_ADJECTIVES = {
    "woody": "grounded",
    "floral": "soft",
    "citrus": "bright",
    "amber": "warm",
    "aromatic": "fresh",
    "leather": "bold",
    "aquatic": "crisp",
    "oriental": "rich",
    "gourmand": "indulgent",
    "spicy": "vibrant",
    "musk": "sensual",
    "chypre": "elegant",
    "fougère": "classic",
}

RECOMMENDATION_TEMPLATES = [
    "Opens with {lead} and settles into a {adj} {family} dry-down.",
    "A standout {family} pick — {lead} up front, with real depth.",
    "{lead} lead here, layered over a smooth {family} base.",
    "Built around {lead} for a {adj}, wear-anywhere {family} feel.",
    "Wears easy but leaves an impression — {lead} carry the opening.",
    "One to try on skin: {adj} {family} energy with {lead} at the center.",
    "This leans {adj} and {family}, anchored by {lead}.",
    "Expect {lead} first, then a lingering {family} trail.",
    "A solid {family} option when you want something {adj} — note the {lead}.",
    "Signature-worthy: {lead} woven through a balanced {family} profile.",
    "Approachable yet distinct — {lead} give it immediate character.",
    "For something {adj} in the {family} family, start with the {lead}.",
]


def extract_lead_notes(notes: str, count: int = 2) -> str:
    if not notes or notes == "nan":
        return "distinctive accords"

    parts = [part.strip() for part in notes.split(",") if part.strip()]
    if not parts:
        return "distinctive accords"
    if len(parts) == 1:
        return title_case(parts[0])

    highlighted = [title_case(part) for part in parts[:count]]
    if len(highlighted) == 1:
        return highlighted[0]
    return f"{highlighted[0]} and {highlighted[1]}"


def recommendation_blurb(family: str, notes: str, index: int) -> str:
    family_key = family.strip().lower()
    family_display = title_case(family_key)
    lead = extract_lead_notes(notes)
    adj = FAMILY_ADJECTIVES.get(family_key, "distinctive")
    template = RECOMMENDATION_TEMPLATES[index % len(RECOMMENDATION_TEMPLATES)]

    return template.format(
        family=family_display,
        lead=lead,
        adj=adj,
    )


def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = "landing"


def init_session_state():
    defaults = {
        "step": "landing",
        "selected_family": None,
        "matched_fragrance": None,
        "user_query": "",
        "confirmation_shown": False,
        "redirect_message": None,
        "external_profile": None,
        "match_source": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_styles():
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 640px;
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
            [data-testid="stHeader"], [data-testid="stToolbar"],
            footer, #MainMenu { visibility: hidden; }
            h1 {
                text-align: center;
                font-weight: 600;
                letter-spacing: -0.02em;
                color: #1a1a2e;
                margin-bottom: 0.5rem;
            }
            .subtitle {
                text-align: center;
                color: #6b7280;
                font-size: 1rem;
                margin-bottom: 2rem;
            }
            .rec-card {
                background: linear-gradient(135deg, #fafafa 0%, #f3f4f6 100%);
                border-left: 4px solid #7c3aed;
                border-radius: 12px;
                padding: 1.25rem 1.5rem;
                margin-bottom: 1rem;
            }
            .rec-brand {
                font-size: 0.85rem;
                color: #7c3aed;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .rec-name {
                font-size: 1.25rem;
                font-weight: 700;
                color: #1a1a2e;
                margin: 0.25rem 0;
            }
            .rec-family {
                font-size: 0.9rem;
                color: #4b5563;
                margin-bottom: 0.5rem;
            }
            .rec-notes {
                font-size: 0.95rem;
                color: #374151;
                margin-bottom: 0.75rem;
            }
            .rec-why {
                font-size: 0.9rem;
                color: #6b7280;
                font-style: italic;
            }
            .confirm-box {
                background: #f0fdf4;
                border: 1px solid #86efac;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1.5rem 0;
            }
            .external-box {
                background: #eff6ff;
                border: 1px solid #93c5fd;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1.5rem 0;
            }
            .external-badge {
                display: inline-block;
                background: #dbeafe;
                color: #1d4ed8;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 0.25rem 0.6rem;
                border-radius: 999px;
                margin-bottom: 0.75rem;
            }
            div[data-testid="column"] button {
                width: 100%;
            }
            .stButton > button[kind="primary"] {
                background: #7c3aed;
                border: none;
                border-radius: 10px;
                padding: 0.6rem 2rem;
                font-weight: 600;
            }
            .stButton > button[kind="secondary"] {
                border-radius: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_landing():
    st.title("What is your favorite fragrance?")
    st.markdown(
        '<p class="subtitle">Tell us what you wear — we\'ll find something you\'ll love in-store.</p>',
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Your favorite fragrance",
        placeholder="e.g. Sauvage, Eros, Cloud…",
        label_visibility="collapsed",
        key="landing_input",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Enter", type="primary", use_container_width=True):
            if query.strip():
                st.session_state.user_query = query.strip()
                st.session_state.step = "process_favorite"
                st.rerun()
            else:
                st.warning("Please enter a fragrance name.")

    st.markdown("<br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])
    with center:
        if st.button("I don't have a favorite.", use_container_width=True):
            st.session_state.step = "family_select"
            st.rerun()


def render_external_confirm(profile: dict):
    st.title("We know this one")
    st.markdown(
        f"""
        <div class="external-box">
            <div class="external-badge">Not in our inventory</div>
            <div class="rec-brand">{profile["brand"]}</div>
            <div class="rec-name">{profile["name"]}</div>
            <div class="rec-family"><strong>Profile:</strong> {profile["family"]}</div>
            <div class="rec-notes"><strong>Core Notes:</strong> {profile["notes"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">Here\'s the scent profile — we\'ll match you to similar fragrances we carry in-store.</p>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("See in-store matches", type="primary", use_container_width=True):
            st.session_state.step = "recommendations"
            st.rerun()


def render_favorite_confirm(match: pd.Series, family: str):
    st.title("We found your match")
    st.markdown(
        f"""
        <div class="confirm-box">
            <div class="rec-brand">{title_case(match["brand"])}</div>
            <div class="rec-name">{title_case(match["fragrance name"])}</div>
            <div class="rec-family"><strong>Family:</strong> {title_case(match["primary olfactory family"])}</div>
            <div class="rec-notes"><strong>Core Notes:</strong> {title_case(match["core key notes"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.selected_family = family
    st.session_state.confirmation_shown = True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("See recommendations", type="primary", use_container_width=True):
            st.session_state.step = "recommendations"
            st.rerun()


def render_family_select(df: pd.DataFrame):
    if st.session_state.redirect_message:
        st.info(st.session_state.redirect_message)
        st.session_state.redirect_message = None

    st.title("Choose your vibe")
    st.markdown(
        '<p class="subtitle">Select the scent profile that speaks to you.</p>',
        unsafe_allow_html=True,
    )

    families = get_available_families(df)
    cols_per_row = 2 if len(families) > 4 else 1

    for i in range(0, len(families), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(families):
                family = families[idx]
                with col:
                    if st.button(family, key=f"family_{family}", use_container_width=True):
                        st.session_state.selected_family = family.lower()
                        st.session_state.external_profile = None
                        st.session_state.match_source = "manual"
                        st.session_state.step = "recommendations"
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Over", type="primary", use_container_width=True, key="family_start_over"):
            reset_session()
            st.rerun()


def render_recommendations(df: pd.DataFrame):
    family = st.session_state.selected_family
    if not family:
        st.session_state.step = "landing"
        st.rerun()
        return

    matches = filter_by_family(df, family)
    family_display = title_case(family)

    st.title("Your matches")

    if st.session_state.match_source == "external" and st.session_state.external_profile:
        profile = st.session_state.external_profile
        st.markdown(
            f'<p class="subtitle">Similar to <strong>{profile["brand"]} {profile["name"]}</strong> '
            f'({profile["family"]}) — available in-store now</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p class="subtitle">Based on your <strong>{family_display}</strong> profile</p>',
            unsafe_allow_html=True,
        )

    if matches.empty:
        st.info(f"No in-store matches found for {family_display}. Try another profile.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Choose a different profile", use_container_width=True):
                st.session_state.step = "family_select"
                st.session_state.selected_family = None
                st.rerun()
    else:
        for index, (_, row) in enumerate(matches.iterrows()):
            notes = row["core key notes"]
            st.markdown(
                f"""
                <div class="rec-card">
                    <div class="rec-brand">{title_case(row["brand"])}</div>
                    <div class="rec-name">{title_case(row["fragrance name"])}</div>
                    <div class="rec-family">{title_case(row["primary olfactory family"])}</div>
                    <div class="rec-notes">{title_case(notes)}</div>
                    <div class="rec-why">{recommendation_blurb(family, notes, index)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Over", type="primary", use_container_width=True):
            reset_session()
            st.rerun()


def process_favorite_input(df: pd.DataFrame):
    query = st.session_state.user_query
    match = find_in_inventory(df, query)

    if match is not None:
        st.session_state.matched_fragrance = match.to_dict()
        st.session_state.external_profile = None
        st.session_state.match_source = "inventory"
        family = match["primary olfactory family"]
        st.session_state.selected_family = resolve_family_keyword(family)
        st.session_state.step = "favorite_confirm"
        st.rerun()
        return

    external_profile = lookup_external_fragrance(query)
    if external_profile:
        st.session_state.external_profile = external_profile
        st.session_state.matched_fragrance = None
        st.session_state.match_source = "external"
        st.session_state.selected_family = resolve_family_keyword(external_profile["family"])
        st.session_state.step = "external_confirm"
        st.rerun()
        return

    st.session_state.external_profile = None
    st.session_state.match_source = None
    st.session_state.redirect_message = (
        f"We couldn't find \"{query}\" in our inventory — let's pick a scent profile instead."
    )
    st.session_state.step = "family_select"
    st.rerun()


def main():
    st.set_page_config(
        page_title="Fragrance Finder",
        page_icon="✨",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    init_session_state()

    df = load_inventory()
    step = st.session_state.step

    if step == "landing":
        render_landing()
    elif step == "process_favorite":
        process_favorite_input(df)
    elif step == "favorite_confirm":
        match = pd.Series(st.session_state.matched_fragrance)
        render_favorite_confirm(match, st.session_state.selected_family)
    elif step == "external_confirm":
        render_external_confirm(st.session_state.external_profile)
    elif step == "family_select":
        render_family_select(df)
    elif step == "recommendations":
        render_recommendations(df)


if __name__ == "__main__":
    main()
