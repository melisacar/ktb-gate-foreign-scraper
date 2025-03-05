import os
env = os.getenv("ENV", "docker")

if env == "local":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/ktb-gate-foreign-scrape")
elif env == "docker":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@ktb-gate-foreign-database:5432/ktb-gate-foreign-scrape")
else:
    None

if DATABASE_URL is None:
    raise Exception("DB URL not found")