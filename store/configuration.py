from datetime import timedelta
import os

databaseUrl = os.environ.get("DATABASE_URL") or "storedatabase"
user = os.environ.get("ROOT_USER")  or "root"
password = os.environ.get("ROOT_PASSWORD") or "root"
jwtSecretKey = os.environ.get("JWT_SECRET_KEY") or "1"
redisHost = os.environ.get("REDIS_HOST") or "redis"

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{databaseUrl}/store"
    JWT_SECRET_KEY = jwtSecretKey
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REDIS_HOST = redisHost
    REDIS_PRODUCTS_LIST = "productList"
