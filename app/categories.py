"""Primary gallery categories (spec §45).

These are ordinary Lightroom keywords, tagged on photos the same way as
any other descriptive keyword (Leicester, Night, ...). The website simply
decides that a particular subset gets promoted to top-level nav
categories; every other keyword a photo has becomes a secondary filter.

Each category can have several keyword variants — e.g. a photo tagged
"Object" in Lightroom should still group under "Things" on the website.
Variants are alternate spellings of the SAME category, not sub-categories.

EDIT HERE to change categories or their variants. The dict key is the
category's display name (used for the nav label and the ?category= URL
slug); the list is every keyword variant that should count as that
category — include the display name itself if it should also match.
"""

from slugify import slugify

PRIMARY_CATEGORIES = {
    "Things": ["Thing", "Things", "Object", "Objects"],
    "Places": ["Place", "Places", "Location", "Locations"],
    "People": ["Person", "People"],
}

# Category display name -> URL slug, e.g. "Things" -> "things".
PRIMARY_CATEGORY_SLUGS = {name: slugify(name) for name in PRIMARY_CATEGORIES}

# Category URL slug -> the set of variant slugs that match it, e.g.
# "things" -> {"thing", "things", "object", "objects"}.
PRIMARY_CATEGORY_VARIANT_SLUGS = {
    PRIMARY_CATEGORY_SLUGS[name]: {slugify(variant) for variant in variants}
    for name, variants in PRIMARY_CATEGORIES.items()
}

# Every variant slug across all categories, for excluding primary-category
# keywords from the secondary filter dropdown.
ALL_PRIMARY_VARIANT_SLUGS = {
    slug
    for variant_slugs in PRIMARY_CATEGORY_VARIANT_SLUGS.values()
    for slug in variant_slugs
}
