# Jetbase Configuration
# Builds the database connection string from the project root .env file.

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

sqlalchemy_url = (
    f"postgresql+psycopg://{os.environ['POSTGRES_USER']}"
    f":{os.environ['POSTGRES_PASSWORD']}"
    f"@localhost:{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ['POSTGRES_DB']}"
)
