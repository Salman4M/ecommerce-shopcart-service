from sqlalchemy.orm import Session
from sqlalchemy import String,cast
from . import models, schemas
from pydantic import UUID4

# value of user_uuid will come us when user instance is created (by event on rabbitmq)
# def create_cart_for_user(db: Session,user_uuid:UUID4):
#     cart = models.ShopCart(user_uuid=user_uuid)
#     db.add(cart)
#     db.commit()
#     db.refresh(cart)

#     return cart

#temporary
def create_cart(db: Session, user_uuid: UUID4):
    check_user = db.query(models.ShopCart).filter(models.ShopCart.user_uuid == user_uuid).first()
    if check_user:
        return check_user
    
    db_cart = models.ShopCart(user_uuid = user_uuid)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def get_user_by_uuid(db: Session , user_uuid: UUID4):
    db_check = db.query(models.ShopCart).filter(models.ShopCart.user_uuid==user_uuid).first()
    return db_check


def get_cart(db: Session, uuid: UUID4):
    return db.query(models.ShopCart).filter(models.ShopCart.user_uuid == uuid).first()


def update_cart(db: Session,item_id:int, cart_id: int, item: schemas.CartItemUpdate):
    db_item = db.query(models.CartItem).filter(models.CartItem.shop_cart_id==cart_id,models.CartItem.id==item_id).first()
    if not db_item:
        return None
    db_item.quantity = item.quantity
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_cart_item(db: Session,cart_id: int,item_id: int):
    db_item = db.query(models.CartItem).filter(models.CartItem.shop_cart_id==cart_id, models.CartItem.id == item_id).first()
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item


def add_item_to_cart(db: Session, cart_id: int, item: schemas.CartItemCreate):
    existing_item = (
        db.query(models.CartItem)
        .filter(models.CartItem.shop_cart_id==cart_id,models.CartItem.product_variation_id==item.product_variation_id)
        .first()
    )
    if existing_item:
        existing_item.quantity+=item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    db_item = models.CartItem(shop_cart_id=cart_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


#for gateway
# def get_cart(db:Session, user_uuid: UUID4):
#     db_check = db.query(models.ShopCart).filter(models.ShopCart.user_uuid==user_uuid).first()
#     return db_check

