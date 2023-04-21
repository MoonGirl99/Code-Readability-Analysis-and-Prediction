import pandas as pd
import string
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import wordcloud
from collections import Counter
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer


# Read the data
df = pd.read_csv('final.csv')


nltk.data.path.append('/home/mahshid/nltk_data/corpora/stopwords')

# Download the stopwords corpus from NLTK
stop_words = set(stopwords.words('english'))
nltk.download('punkt')
nltk.download('wordnet')

# Define a function to preprocess text
def preprocess_text(text):

    # Convert to lowercase
    text = text.lower()

    # Tokenize the text into words
    words = word_tokenize(text)


    # Remove Unicode Characters
    text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", " ", text)
    text = re.sub(r"(@\[A-Za-z0-9]|^rt|http.+?)|(git-svn-id)|(://svn.apache.org/repos/asf/jakarta)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text)
    
    # Remove Digit
    new_str = ""

    for c in text:
        if c.isdigit():
            new_str += " "
        else:
            new_str += c

    text = new_str

    text = " ".join([word for word in text.split() if len(word) > 2])


    p = [
        "fbbffaedef", "sandbox", "trunk", "license" , "bcel" , "vfs" , "apache" , "contact" , "address", "svn", "https", "www", "org", "com",
        "net", "http", "id", "gitsvnid", "tags", "branches", "jakarta", "codec", "commons","git", "license",
        "ffaedef", "ffa", "edef", "and", "for", "the"]

    text = list(filter(lambda x: x not in p, text.split()))
    


    # Remove stop wordsze(text)
    words = [word for word in str(text).split() if word not in stop_words]
    
    # Stem the words
    stemmer = SnowballStemmer('english')
    words = [stemmer.stem(word) for word in words]

    
    # Lemmatize the words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]


    text = " ".join(text)
    return text


# Create a new dataframe for commits with improved readability
df_improved = df[df['readability'] > 0].copy()
# Preprocess the commit messages in the improved readability dataframe
df_improved['preprocessed_commit_msg'] = df_improved['commit_msg'].apply(preprocess_text)

# frequency of words
text_frequency = df_improved['commit_msg'].apply(preprocess_text).str.split(expand=True).stack()
text_frequency = Counter(text_frequency)
most_common_words = text_frequency.most_common(5)
frequency = pd.DataFrame(most_common_words, columns=['word', 'frequency'])

plt.bar(frequency['word'], frequency['frequency'])
plt.show()


# Create a Wordcloud for improved readability
improved_wordcloud = wordcloud.WordCloud(collocations = False, background_color='white').generate(' '.join(df_improved['preprocessed_commit_msg']))
plt.imshow(improved_wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# Create a new dataframe for commits with decreased readability
df_decreased = df[df['readability'] < 0].copy()
# Preprocess the commit messages in the decreased readability dataframe
df_decreased['preprocessed_commit_msg'] = df_decreased['commit_msg'].apply(preprocess_text)

# frequency of words
text_frequency = df_decreased['commit_msg'].apply(preprocess_text).str.split(expand=True).stack()
text_frequency = Counter(text_frequency)
most_common_words = text_frequency.most_common(5)
frequency = pd.DataFrame(most_common_words, columns=['word', 'frequency'])

plt.bar(frequency['word'], frequency['frequency'])
plt.show()


# Create a Wordcloud for decreased readability
decreased_wordcloud = wordcloud.WordCloud(collocations= False, background_color='white').generate(' '.join(df_decreased['preprocessed_commit_msg']))
plt.imshow(decreased_wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
