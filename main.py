from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Product
from database import SessionLocal, engine
import database_models

# 1. Tạo tất cả các bảng trong PostgreSQL nếu chưa tồn tại
database_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dữ liệu khởi tạo ban đầu
initial_products = [
    Product(id=1, name="Phone", price=10.99, description="A smartphone with a 6-inch display", quantity=100),
    Product(id=2, name="Laptop", price=999.99, description="A powerful laptop for work and play", quantity=50),
    Product(id=3, name="Headphones", price=49.99, description="Noise-cancelling headphones for immersive sound", quantity=200),
    Product(id=4, name="Smartwatch", price=199.99, description="A smartwatch with fitness tracking features", quantity=75),
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Hàm khởi tạo dữ liệu vào PostgreSQL
def init_db():
    db = SessionLocal()
    try:
        # Kiểm tra nếu bảng chưa có dữ liệu thì mới thêm vào
        if db.query(database_models.Product).count() == 0:
            for product in initial_products:
                db_product = database_models.Product(**product.model_dump())
                db.add(db_product)
            db.commit()
    finally:
        db.close()

init_db()


@app.get("/")
def greet():
    return "Hello, welcome to the FastAPI demo project!"


@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    # db: Session = Depends(get_db) -> Yêu cầu FastAPI tiêm DB session vào đây
    db_products = db.query(database_models.Product).order_by(database_models.Product.id.asc()).all()
    return db_products


@app.get("/product/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    # Tìm sản phẩm đầu tiên có ID khớp với param 'id' truyền vào
    db_product = (
        db.query(database_models.Product)
        .filter(database_models.Product.id == id)
        .first()
    )
    # Nếu tìm thấy thì trả về, nếu không tìm thấy thì trả về thông báo lỗi
    if db_product:
        return db_product
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/product")
def add_product(product: Product, db: Session = Depends(get_db)):
    db = SessionLocal()
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
   

@app.put("/product/{id}")
def update_product(id: int, product: Product):
    db = SessionLocal()
    try:
        db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        
        db.commit()
        return {"message": "Product updated successfully"}
    finally:
        db.close()


@app.delete("/product/{id}")
def delete_product(id: int):
    db = SessionLocal()
    try:
        db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    finally:
        db.close()