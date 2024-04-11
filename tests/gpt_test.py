from models.gpt import GPT


def returns_response():
    gpt = GPT(True)
    response = gpt.query("Hello, how are you?", "")

    assert response is not None


if __name__ == "__main__":
    returns_response()
