from sqlalchemy.orm import Session

from app.domains.taxonomy.models import TaxonomyGroup, TaxonomyValue

DEMO_TAXONOMY_GROUPS = [
    {
        "key": "clothing-type",
        "label": "Loại quần áo",
        "sort_order": 0,
        "values": [
            {"key": "ao", "label": "Áo"},
            {"key": "quan", "label": "Quần"},
            {"key": "vay", "label": "Váy"},
            {"key": "dam", "label": "Đầm"},
            {"key": "ao-khoac", "label": "Áo khoác"},
        ],
    },
    {
        "key": "occasion",
        "label": "Loại dịp",
        "sort_order": 1,
        "values": [
            {"key": "hang-ngay", "label": "Hằng ngày"},
            {"key": "di-lam", "label": "Đi làm"},
            {"key": "du-tiec", "label": "Dự tiệc"},
            {"key": "di-bien", "label": "Đi biển"},
        ],
    },
    {
        "key": "style",
        "label": "Loại phong cách",
        "sort_order": 2,
        "values": [
            {"key": "casual", "label": "Casual"},
            {"key": "minimalist", "label": "Minimalist"},
            {"key": "street", "label": "Street"},
            {"key": "formal", "label": "Formal"},
        ],
    },
]


def seed_demo_taxonomy_groups(db: Session) -> None:
    if db.query(TaxonomyGroup).count() > 0:
        return
    for group_data in DEMO_TAXONOMY_GROUPS:
        group = TaxonomyGroup(key=group_data["key"], label=group_data["label"], sort_order=group_data["sort_order"])
        for index, value_data in enumerate(group_data["values"]):
            group.values.append(TaxonomyValue(key=value_data["key"], label=value_data["label"], sort_order=index))
        db.add(group)
    db.commit()
