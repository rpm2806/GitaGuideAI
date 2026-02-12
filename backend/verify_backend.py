
import sys
import os

print("Verifying Backend Codebase...")
try:
    print("Importing main...")
    import main
    print("Importing rag...")
    import rag
    print("Importing safety...")
    import safety
    print("Backend verification successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
