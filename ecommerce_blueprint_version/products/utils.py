
from ecommerce_blueprint_version.models import Product, ProductCategory, Category


def getAllProducts():
    products = Product.query.join(ProductCategory, Product.productid == ProductCategory.productid) \
        .join(Category, Category.categoryid == ProductCategory.categoryid) \
        .order_by(Category.categoryid.desc()) \
        .all()
    return products


def getProductByProductId(productId):
    productByProductId = Product.query.filter(
        Product.productid == productId).first()
    return productByProductId


def getProductsByCategoryId(categoryId):
    products_by_categoryId = Product.query.join(ProductCategory, Product.productid == ProductCategory.productid) \
        .join(Category, Category.categoryid == ProductCategory.categoryid) \
        .filter(Category.categoryid == int(categoryId)) \
        .all()
    return products_by_categoryId
        # .add_columns(Category.categoryid, Category.category_name_zh, Category.category_name_en, Category.category_name_fr, Category.category_img) \


def getPriceRangeFromVariants(variants):
    max, min = float(variants[0].get("variant_price")), float(variants[0].get("variant_price"))
    for variant in variants:
        print('price', variant, variant.get("variant_price"))
        price = float(variant.get("variant_price"))
        if price > max:
            max = price
        elif price < min:
            min = price
    return (min, max)

