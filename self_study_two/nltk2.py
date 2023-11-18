import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import word_tokenize, sent_tokenize

# nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

text = """Welcome you to programming knowledge. Lets start with our first tutorial on NLTK. We shall learn the basics of NLTK here."""
demoWords = ["playing", "happiness", "going", "doing", "yes", "no", "I", "having", "had", "haved"]

tokenize_words = word_tokenize(text)
# print(words)

without_stop_words = []
for word in tokenize_words:
    if word not in stop_words:
        without_stop_words.append(word)
print(set(tokenize_words) - set(without_stop_words))
print(tokenize_words)
print(without_stop_words)