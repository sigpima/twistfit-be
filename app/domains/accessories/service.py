from sqlalchemy.orm import Session

from app.domains.accessories.models import AccessoryProduct
from app.domains.accessories.schemas import AccessoryProductInput


def list_accessories(db: Session) -> list[AccessoryProduct]:
    return db.query(AccessoryProduct).order_by(AccessoryProduct.id.desc()).all()


def get_accessory(db: Session, accessory_id: int) -> AccessoryProduct | None:
    return db.get(AccessoryProduct, accessory_id)


def create_accessory(db: Session, data: AccessoryProductInput) -> AccessoryProduct:
    accessory = AccessoryProduct(**data.model_dump())
    db.add(accessory)
    db.commit()
    db.refresh(accessory)
    return accessory


def update_accessory(db: Session, accessory_id: int, data: AccessoryProductInput) -> AccessoryProduct | None:
    accessory = get_accessory(db, accessory_id)
    if accessory is None:
        return None
    for field, value in data.model_dump().items():
        setattr(accessory, field, value)
    db.commit()
    db.refresh(accessory)
    return accessory


def delete_accessory(db: Session, accessory_id: int) -> bool:
    accessory = get_accessory(db, accessory_id)
    if accessory is None:
        return False
    db.delete(accessory)
    db.commit()
    return True


def _score(product: AccessoryProduct, occasion: str, style: str, tone: str | None) -> int:
    score = 0
    if occasion in product.occasion_tags:
        score += 2
    if tone is not None and tone in product.tone_tags:
        score += 2
    if style in product.style_tags:
        score += 1
    return score


def _select_recommendations(
    products: list[AccessoryProduct], occasion: str, style: str, tone: str | None, limit: int
) -> list[AccessoryProduct]:
    best_by_category: dict[str, tuple[AccessoryProduct, int]] = {}
    for product in products:
        score = _score(product, occasion, style, tone)
        if score <= 0:
            continue
        current = best_by_category.get(product.category)
        if (
            current is None
            or score > current[1]
            or (score == current[1] and product.created_at > current[0].created_at)
        ):
            best_by_category[product.category] = (product, score)

    if not best_by_category:
        # Nothing scored at all (e.g. a freshly-seeded catalog that
        # doesn't cover this occasion/style/tone yet) — surface the
        # newest active item per category instead of an empty section.
        newest_by_category: dict[str, AccessoryProduct] = {}
        for product in products:
            current = newest_by_category.get(product.category)
            if current is None or product.created_at > current.created_at:
                newest_by_category[product.category] = product
        ranked = sorted(newest_by_category.values(), key=lambda item: item.created_at, reverse=True)
        return ranked[:limit]

    ranked = sorted(best_by_category.values(), key=lambda pair: pair[1], reverse=True)
    return [product for product, _matched_score in ranked][:limit]


def recommend(db: Session, occasion: str, style: str, tone: str | None, limit: int = 6) -> list[AccessoryProduct]:
    products = db.query(AccessoryProduct).filter(AccessoryProduct.is_active.is_(True)).all()
    return _select_recommendations(products, occasion, style, tone, limit)
