import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PERSIST_DIR = os.path.join(PROJECT_ROOT, "chroma_web_chatbot")

print(BASE_DIR)
print(PERSIST_DIR)