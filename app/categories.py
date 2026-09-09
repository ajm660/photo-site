"""Primary gallery categories (spec §45).

These are ordinary Lightroom keywords, tagged on photos the same way as
any other descriptive keyword (Leicester, Night, ...). The website simply
decides that this particular subset gets promoted to top-level nav
categories; every other keyword a photo has becomes a secondary filter.
"""

from slugify import slugify

PRIMARY_CATEGORIES = ["Things", "Objects", "Places", "People", "Nature"]
PRIMARY_CATEGORY_SLUGS = [slugify(name) for name in PRIMARY_CATEGORIES]
PRIMARY_CATEGORY_SLUG_SET = set(PRIMARY_CATEGORY_SLUGS)
