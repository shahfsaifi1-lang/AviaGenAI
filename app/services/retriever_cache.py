import pickle

_retriever = None
def get_retriever():
    global _retriever
    if _retriever is None:
        with open("artifacts/retriever.pkl", "rb") as f:
            _retriever = pickle.load(f)
    return _retriever

