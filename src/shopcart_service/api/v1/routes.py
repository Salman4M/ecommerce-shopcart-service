from fastapi import APIRouter, Depends,HTTPException,Request
from sqlalchemy.orm import Session
from src.shopcart_service import crud, schemas
from src.shopcart_service.core import db
from src.shopcart_service import models
from pydantic import UUID4
from src.shopcart_service.core.auth import get_user_from_gateway, User  # Import here!

router = APIRouter(prefix="/shopcart/api", tags=["Cart"])

#####TESTING AUTHENTICATION

@router.post("/", response_model=schemas.ShopCartRead)
def create_cart(
    current_user: User = Depends(get_user_from_gateway),  # Add this!
    db: Session = Depends(db.get_db)
):
    existing_cart = crud.get_user_by_uuid(db, current_user.user_uuid)  # Use current_user.user_uuid
    if existing_cart:
        raise HTTPException(status_code=400, detail="You already have a shopping cart")
    return crud.create_cart(db, current_user.user_uuid)


@router.get("/mycart", response_model=schemas.ShopCartRead)
def get_cart(
    current_user: User = Depends(get_user_from_gateway),  
    db: Session = Depends(db.get_db)
):
    """Get current user's shopping cart"""
    cart = crud.get_cart(db, current_user.user_uuid) 
    if not cart:
        cart = crud.create_cart(db, current_user.user_uuid)
    return cart


@router.post("/{cart_id}/items/{product_var_uuid}", response_model=schemas.CartItemRead)
async def add_item(
    cart_id: int,
    product_var_uuid: UUID4,
    item: schemas.CartItemCreate,
    current_user: User = Depends(get_user_from_gateway), 
    db: Session = Depends(db.get_db)
):

    cart = crud.get_cart(db, current_user.user_uuid)
    if not cart or cart.id != cart_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this cart")
    
    return await crud.add_item_to_cart(db, product_var_uuid, cart_id, item)



@router.put("/{cart_id}/items/{item_id}", response_model=schemas.CartItemRead)
def update_cart_item(
    cart_id: int,
    item_id: int,
    item: schemas.CartItemUpdate,
    current_user: User = Depends(get_user_from_gateway),
    db: Session = Depends(db.get_db)
):
    cart = crud.get_cart(db, current_user.user_uuid)
    if not cart or cart.id != cart_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this cart")
    
    updated_item = crud.update_cart(db, item_id, cart_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return updated_item


@router.delete("/{cart_id}/items/{item_id}", response_model=schemas.CartItemRead)
def delete_cart_item(
    cart_id: int,
    item_id: int,
    current_user: User = Depends(get_user_from_gateway),  
    db: Session = Depends(db.get_db)
):
    cart = crud.get_cart(db, current_user.user_uuid)
    if not cart or cart.id != cart_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this cart")
    
    deleted_item = crud.delete_cart_item(db, item_id, cart_id)
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return deleted_item



# @router.post("/", response_model=schemas.ShopCartRead)
# def create_cart(user_uuid: UUID4, db: Session = Depends(db.get_db)):
#     existing_cart = crud.get_user_by_uuid(db,user_uuid)
#     if existing_cart:
#         raise HTTPException(status_code = 401 , detail = "You have already got a shop cart")
#     return crud.create_cart(db, user_uuid)


# @router.get("/mycart", response_model=schemas.ShopCartRead)
# def get_cart(user_uuid: UUID4, db: Session = Depends(db.get_db)):
#     cart = crud.get_cart(db, user_uuid)
#     if not cart:
#         new_cart = crud.create_cart(db,user_uuid)
#         return new_cart
#     return cart


# @router.post("/{cart_id}/items/{product_var_id}", response_model=schemas.CartItemRead)
# def add_item(cart_id: int,product_var_id: int, item: schemas.CartItemCreate, db: Session = Depends(db.get_db)):
#     return crud.add_item_to_cart(db, product_var_id, cart_id, item)



# @router.put("/{cart_id}/items/{item_id}",response_model = schemas.CartItemRead)
# def update_cart_item(cart_id:int, item_id:int, item: schemas.CartItemUpdate, db: Session = Depends(db.get_db)):
#     updated_item = crud.update_cart(db,item_id,cart_id,item)
#     if not updated_item:
#         raise HTTPException(status_code=404, detail = "Cart item not found")
#     return updated_item


# @router.delete("/{cart_id}/items/{item_id}",response_model = schemas.CartItemRead)
# def delete_cart_item(cart_id: int, item_id: int, db:Session = Depends(db.get_db)):
#     deleted_item = crud.delete_cart_item(db, item_id, cart_id)
#     if not deleted_item:
#         raise HTTPException(status_code=404, detail="Cart item not found")
#     return deleted_item



