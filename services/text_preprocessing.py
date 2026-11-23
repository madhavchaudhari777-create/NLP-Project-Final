
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK resources
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("punkt_tab")

STOP_WORDS = set(stopwords.words("english"))


def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Preserve common Big-O expressions before cleaning
    text = re.sub(
        r"o\s*\(\s*([a-z0-9]+\s*(?:\^\s*\d+)?)\s*\)",
        r"o\1",
        text
    )

    # Preserve technical characters
    text = re.sub(r"[^a-z0-9\s+#./^-]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text




def tokenize_text(text):
    return re.findall(
        r"o[a-z0-9]+(?:\^[0-9]+)?|c\+\+|c#|"
        r"[a-z0-9]+(?:[./+#-][a-z0-9+#-]+)*",
        text
    )



def remove_stopwords(tokens):
    return [
        word for word in tokens
        if word not in STOP_WORDS
    ]


def preprocess_text(text):
    cleaned = clean_text(text)
    tokens = tokenize_text(cleaned)
    filtered_tokens = remove_stopwords(tokens)

    return " ".join(filtered_tokens)



if __name__ == "__main__":

    samples = [
        "I use C++ and C# for programming.",
        "The server IP address is 192.168.1.1",
        "The time complexity is O(n^2).",
        "Python is used for Artificial Intelligence!"
    ]

    for sample in samples:
        print("\nOriginal:", sample)
        print("Cleaned:", clean_text(sample))
        print("Tokens:", tokenize_text(clean_text(sample)))
        print("After Stopword Removal:", preprocess_text(sample))

