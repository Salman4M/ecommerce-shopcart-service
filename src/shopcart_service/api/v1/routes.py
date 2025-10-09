from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from src.shopcart_service import crud, schemas
from src.shopcart_service.core import db
from requests import Request
router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=schemas.ShopCartRead)
def create_cart(cart: schemas.ShopCartCreate, db: Session = Depends(db.get_db)):
    existed = crud.get_user_by_uuid(db,cart.user_uuid)
    if existed:
        raise HTTPException(status_code = 400, detail = "user has already created")
    return crud.create_cart(db, cart)

# @router.get("/mycart", response_model=schemas.ShopCartRead)
# def read_carts(user_uuid: UUID, db: Session = Depends(db.get_db)):
#     cart = crud.get_cart(db, user_uuid)
#     if not cart:
#         raise HTTPException(status_code=404, detail="Cart not found")
#     return cart

@router.get("/mycart/{cart_id}", response_model=schemas.ShopCartRead)
def get_cart(cart_id: int, db: Session = Depends(db.get_db)):
    cart = crud.get_cart(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.post("mycart/{cart_id}/items/", response_model=schemas.CartItemRead)
def add_item(cart_id: int, item: schemas.CartItemCreate, db: Session = Depends(db.get_db)):
    return crud.add_item_to_cart(db, cart_id, item)

##from gateway
@router.post("mycart/{cart_id}/items/", response_model=schemas.CartItemRead)
def add_item(cart_id: int, item: schemas.CartItemCreate, request: Request, db: Session = Depends(db.get_db)):
    user_uuid = request.headers.get("X-User-Uuid")
    if not user_uuid:
        raise HTTPException(status = 401, detail = "User is not authenticated")
    return crud.add_item_to_cart(db,cart_id,item)



@router.put("/mycart/{cart_id}/items/{item_id}",response_model = schemas.CartItemRead)
def update_cart_item(cart_id:int, item_id:int, item: schemas.CartItemUpdate, db: Session = Depends(db.get_db)):
    updated_item = crud.update_cart(db,item_id,cart_id,item)
    if not updated_item:
        raise HTTPException(status_code=404, detail = "Cart item not found")
    return updated_item

@router.delete("/mycart/{cart_id}/items/{item_id}",response_model = schemas.CartItemRead)
def delete_cart_item(cart_id: int, item_id: int, db:Session = Depends(db.get_db)):
    deleted_item = crud.delete_cart_item(cart_id,item_id, db )
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return deleted_item
