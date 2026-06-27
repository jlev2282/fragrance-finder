import re

import pandas as pd
import streamlit as st

# Popular fragrances not in store inventory — mapped to olfactory family keywords
EXTERNAL_FRAGRANCES = {
    "sauvage": "aromatic",
    "dior sauvage": "aromatic",
    "eros": "amber",
    "versace eros": "amber",
    "bleu de chanel": "woody aromatic",
    "acqua di gio": "aquatic",
    "light blue": "citrus",
    "dolce light blue": "citrus",
    "black opium": "oriental",
    "good girl": "floral",
    "carolina herrera good girl": "floral",
    "libre": "floral",
    "ysl libre": "floral",
    "lost cherry": "gourmand",
    "tom ford lost cherry": "gourmand",
    "baccarat rouge 540": "amber",
    "creed aventus": "woody",
    "1 million": "spicy",
    "paco rabanne 1 million": "spicy",
    "angel": "gourmand",
    "thierry mugler angel": "gourmand",
    "la vie est belle": "floral",
    "flowerbomb": "floral",
    "viktor rolf flowerbomb": "floral",
    "chanel no 5": "floral",
    "no. 5": "floral",
    "miss dior": "floral",
    "jo malone wood sage": "woody",
    "tom ford oud wood": "woody",
    "by the fireplace": "woody",
    "le male": "aromatic",
    "jean paul gaultier le male": "aromatic",
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


def lookup_external_fragrance(query: str) -> str | None:
    query = query.strip().lower()
    if not query:
        return None

    if query in EXTERNAL_FRAGRANCES:
        return EXTERNAL_FRAGRANCES[query]

    for name, family in EXTERNAL_FRAGRANCES.items():
        if name in query or query in name:
            return family

    return None


def filter_by_family(df: pd.DataFrame, family: str) -> pd.DataFrame:
    family = family.strip().lower()
    mask = df["primary olfactory family"].str.contains(family, case=False, na=False)
    return df[mask].copy()


def why_youll_love_it(family: str, notes: str) -> str:
    family_display = title_case(family)
    notes_display = title_case(notes) if notes else "distinctive accords"
    return (
        f"If you love {family_display}, this selection features beautiful notes of "
        f"{notes_display}."
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
                        st.session_state.step = "recommendations"
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
        for _, row in matches.iterrows():
            notes = row["core key notes"]
            st.markdown(
                f"""
                <div class="rec-card">
                    <div class="rec-brand">{title_case(row["brand"])}</div>
                    <div class="rec-name">{title_case(row["fragrance name"])}</div>
                    <div class="rec-family">{title_case(row["primary olfactory family"])}</div>
                    <div class="rec-notes">{title_case(notes)}</div>
                    <div class="rec-why">{why_youll_love_it(family, notes)}</div>
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
        family = match["primary olfactory family"]
        for keyword in FAMILY_KEYWORDS:
            if keyword.lower() in family:
                st.session_state.selected_family = keyword.lower()
                break
        else:
            st.session_state.selected_family = family.split()[0]
        st.session_state.step = "favorite_confirm"
        st.rerun()
        return

    external_family = lookup_external_fragrance(query)
    if external_family:
        for keyword in FAMILY_KEYWORDS:
            if keyword.lower() in external_family:
                st.session_state.selected_family = keyword.lower()
                st.session_state.step = "recommendations"
                st.rerun()
                return
        st.session_state.selected_family = external_family
        st.session_state.step = "recommendations"
        st.rerun()
        return

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
    elif step == "family_select":
        render_family_select(df)
    elif step == "recommendations":
        render_recommendations(df)


if __name__ == "__main__":
    main()
