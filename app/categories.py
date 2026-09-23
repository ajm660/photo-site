"""Primary gallery categories (spec §45).

These are ordinary Lightroom keywords, tagged on photos the same way as
any other descriptive keyword (Leicester, Night, ...). The website simply
decides that a particular subset gets promoted to top-level nav
categories; every other keyword a photo has becomes a secondary filter.

Each category can have several keyword variants — e.g. a photo tagged
"Object" in Lightroom should still group under "Objects" on the website.
Variants are alternate spellings of the SAME category, not sub-categories.

EDIT HERE to change categories or their variants. The dict key is the
category's display name (used for the nav label and the ?category= URL
slug); the list is every keyword variant that should count as that
category — include the display name itself if it should also match.
"""

from slugify import slugify

PRIMARY_CATEGORIES = {
    "People": ["Person", "People"],
    "Architecture & Urban": ["Architecture", "Urban", "Architecture & Urban"],
    "Landscape & Nature": ["Landscape", "Nature", "Landscape & Nature"],
    "Objects": ["Object", "Objects"],
    "Abstract": ["Abstract"],
}

# Shorter display names shown on narrow (mobile) viewports, where the full
# name would wrap or crowd the nav. Categories not listed here just use
# their full name at every width.
PRIMARY_CATEGORY_SHORT_NAMES = {
    "Architecture & Urban": "Urban",
    "Landscape & Nature": "Nature",
}

# The Lightroom keyword used to mark a photo as ready for the website —
# every photo exported for the site should carry it. The "All" pseudo
# category filters on this keyword directly instead of assuming every row
# in the database is meant to be shown.
WEB_KEYWORD_SLUG = slugify("web")

# URL slug for the "All" pseudo category, shown as the first button.
ALL_CATEGORY_SLUG = "all"

# Category display name -> URL slug, e.g. "Objects" -> "objects".
PRIMARY_CATEGORY_SLUGS = {name: slugify(name) for name in PRIMARY_CATEGORIES}

# Category URL slug -> the set of variant slugs that match it, e.g.
# "objects" -> {"object", "objects"}.
PRIMARY_CATEGORY_VARIANT_SLUGS = {
    PRIMARY_CATEGORY_SLUGS[name]: {slugify(variant) for variant in variants}
    for name, variants in PRIMARY_CATEGORIES.items()
}

# Every variant slug across all categories, for excluding primary-category
# keywords from the secondary keyword filter.
ALL_PRIMARY_VARIANT_SLUGS = {
    slug
    for variant_slugs in PRIMARY_CATEGORY_VARIANT_SLUGS.values()
    for slug in variant_slugs
}
