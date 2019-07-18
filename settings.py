from pathlib import Path  # python3 only
from dotenv import load_dotenv
load_dotenv(verbose=True)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
