import os
import httpx
from sqlalchemy.orm import Session
from sqlalchemy import String,cast
from . import models, schemas
from pydantic import UUID4
from fastapi import HTTPException



PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE', 'http://product_service:8000')


async def verify_product_stock(product_var_uuid: UUID4, requested_quantity: int) -> dict:

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f'{PRODUCT_SERVICE_URL}/api/v1/variations/{product_var_uuid}'
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Product variation {product_var_uuid} not found"
                )
            
            response.raise_for_status()
            variation = response.json()
            
            if not variation.get('product', {}).get('is_active', False):
                raise HTTPException(
                    status_code=400,
                    detail="This product is currently unavailable"
                )
            
            available_stock = variation.get('amount', 0)
            if available_stock < requested_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Only {available_stock} items available"
                )
            
            # amount_limit = variation.get('amount_limit', 0)
            # if amount_limit > 0 and requested_quantity > amount_limit:
            #     raise HTTPException(
            #         status_code=400,
            #         detail=f"Maximum {amount_limit} items allowed per order"
            #     )
            
            return variation
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Product service unavailable: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error from product service: {e.response.text}"
        )



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


async def update_cart(db: Session,item_id:int, cart_id: int, item: schemas.CartItemUpdate):
    db_item = db.query(models.CartItem).filter(models.CartItem.shop_cart_id==cart_id,models.CartItem.id==item_id).first()
    if not db_item:
        return None
    
    await verify_product_stock(db_item.product_variation_uuid, item.quantity)

    db_item.quantity = item.quantity
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_cart_item(db: Session, item_id: int,cart_id: int):
    db_item = db.query(models.CartItem).filter(models.CartItem.shop_cart_id==cart_id, models.CartItem.id == item_id).first()
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item


async def add_item_to_cart(db: Session,product_var_uuid: UUID4, cart_id: int, item: schemas.CartItemCreate):
    await verify_product_stock(product_var_uuid, item.quantity)
    
    existing_item = (
        db.query(models.CartItem)
        .filter(models.CartItem.shop_cart_id==cart_id,models.CartItem.product_variation_uuid==product_var_uuid)
        .first()
    )
    if existing_item:
        new_quantity = existing_item.quantity + item.quantity
        await verify_product_stock(product_var_uuid, new_quantity)
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    db_item = models.CartItem(shop_cart_id=cart_id, product_variation_uuid = product_var_uuid, quantity = item.quantity)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


#for gateway
# def get_cart(db:Session, user_uuid: UUID4):
#     db_check = db.query(models.ShopCart).filter(models.ShopCart.user_uuid==user_uuid).first()
#     return db_check

