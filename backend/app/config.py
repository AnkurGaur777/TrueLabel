import os
from dotenv import load_dotenv

load_dotenv()

USDA_FDC_API_KEY = os.getenv("USDA_FDC_API_KEY")
