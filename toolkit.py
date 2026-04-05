import os
from typing import List

class KnowledgeBase:
    """
    Simple RAG system for the Cyber Knowledge Base.
    """
    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = knowledge_dir
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir)

    def search(self, query: str) -> str:
        results = []
        query_tokens = query.lower().split()

        for root, _, files in os.walk(self.knowledge_dir):
            for file in files:
                if file.endswith(".txt") or file.endswith(".md"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if any(t in content.lower() for t in query_tokens):
                                results.append(content[:300])
                    except:
                        continue

        return "\n\n".join(results[:3]) if results else "No relevant data found."


class CTFToolkit:
    """
    Simple toolkit for MVP version.
    """

    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.rag = KnowledgeBase(knowledge_dir=os.path.join(os.getcwd(), "knowledge"))

    def inspect_file(self, file_path: str) -> str:
        target_path = os.path.join(self.workspace_dir, file_path)

        if not os.path.exists(target_path):
            return "File not found."

        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(500)
        except Exception as e:
            return f"Error: {str(e)}"