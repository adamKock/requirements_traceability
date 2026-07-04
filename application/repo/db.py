import os
from psycopg_pool import AsyncConnectionPool

DB_POOL = AsyncConnectionPool(
    conninfo=(
        f"host={os.getenv('DB_HOST')} "
        f"dbname={os.getenv('DB_NAME')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASSWORD')} "
        f"port={os.getenv('DB_PORT')}"
    ),
    min_size=2,
    max_size=10,
    open=False,  # open explicitly in lifespan, not at import time
)

async def open_pool():
    await DB_POOL.open()

async def close_pool():
    await DB_POOL.close()