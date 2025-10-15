from fastapi import APIRouter, Depends,HTTPException,Request
from sqlalchemy.orm import Session
from src.shopcart_service import crud, schemas
from src.shopcart_service.core import db
from src.shopcart_service import models
from pydantic import UUID4
router = APIRouter(prefix="/shopcart", tags=["Cart"])

@router.post("/", response_model=schemas.ShopCartRead)
def create_cart(user_uuid: UUID4, db: Session = Depends(db.get_db)):
    existing_cart = crud.get_user_by_uuid(db,user_uuid)
    if existing_cart:
        raise HTTPException(status_code = 401 , detail = "You have already got a shop cart")
    return crud.create_cart(db, user_uuid)



@router.get("/mycart", response_model=schemas.ShopCartRead)
def get_cart(user_uuid: UUID4, db: Session = Depends(db.get_db)):
    cart = crud.get_cart(db, user_uuid)
    if not cart:
        new_cart = crud.create_cart(db,user_uuid)
        return new_cart
    return cart




@router.post("/{cart_id}/items/{product_var_id}", response_model=schemas.CartItemRead)
def add_item(cart_id: int,product_var_id: int, item: schemas.CartItemCreate, db: Session = Depends(db.get_db)):
    return crud.add_item_to_cart(db, product_var_id, cart_id, item)



@router.put("/{cart_id}/items/{item_id}",response_model = schemas.CartItemRead)
def update_cart_item(cart_id:int, item_id:int, item: schemas.CartItemUpdate, db: Session = Depends(db.get_db)):
    updated_item = crud.update_cart(db,item_id,cart_id,item)
    if not updated_item:
        raise HTTPException(status_code=404, detail = "Cart item not found")
    return updated_item



@router.delete("/{cart_id}/items/{item_id}",response_model = schemas.CartItemRead)
def delete_cart_item(cart_id: int, item_id: int, db:Session = Depends(db.get_db)):
    deleted_item = crud.delete_cart_item(db, item_id, cart_id)
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return deleted_item



#for gateway

# @router.post("/", response_model=schemas.ShopCartRead)
# def create_cart(request: Request, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     return crud.create_cart(db, user_uuid)

# @router.get("/mycart/{cart_id}", response_model=schemas.ShopCartRead)
# def get_cart(cart_id: int,request: Request, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(status = 401, detail=("User is not authenticated"))
#     cart = crud.get_cart(db, cart_id)
#     if not cart:
#         raise HTTPException(status_code=404, detail="Cart not found")
#     return cart

#or 

# @router.get("/{cart_id}", response_model=schemas.ShopCartRead)
# def get_cart(request: Request, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(status_code = 401, detail=("User is not authenticated"))
#     cart = crud.get_cart(db, user_uuid)
#     if not cart:
#         create_cart(db,user_uuid)
#     return crud.get_cart(db,user_uuid)


# @router.post("/items", response_model=schemas.CartItemRead)
# def add_item(request: Request, item: schemas.CartItemCreate, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(401, "User not authenticated")
    
#     cart = crud.get_user_by_uuid(db, user_uuid)
#     if not cart:
#         cart = crud.create_cart(db, user_uuid)

#     return crud.add_item_to_cart(db, cart.id, item)


# @router.put("/items/update/{item_id}", response_model=schemas.CartItemRead)
# def update_item(item_id: int, request: Request, item: schemas.CartItemUpdate, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(401, "User not authenticated")
    
#     cart = crud.get_cart(db,user_uuid)
#     if not cart:
#         raise HTTPException(404, "Cart not found")

#     return crud.update_cart_item(db, cart.id, item_id, item)

# @router.delete("/items/delete/{item_id}", response_model=schemas.CartItemRead)
# def delete_item(item_id: int, request: Request, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(401, "User not authenticated")
    
#     cart = crud.get_cart(db,user_uuid)
#     if not cart:
#         raise HTTPException(404, "Cart not found")

#     return crud.delete_cart_item(db, cart.id, item_id)

# @router.post("mycart/{cart_id}/items/", response_model=schemas.CartItemRead)
# def add_item(cart_id: int, item: schemas.CartItemCreate, request: Request, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(status = 401, detail = "User is not authenticated")
#     return crud.add_item_to_cart(db,cart_id,item)




# @router.get("/tester/{cart_id}", response_model=schemas.ShopCartRead)
# def get_cart(Request, db: Session = Depends(db.get_db)):
#     user_uuid = request.headers.get("X-User-Uuid")
#     if not user_uuid:
#         raise HTTPException(status = 401, detail=("User is not authenticated"))
#     cart = crud.get_cart(db, user_uuid)
#     if not cart:
#         create_cart(db,user_uuid)
#     return crud.get_cart(db,user_uuid)