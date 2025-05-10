import os
import pandas as pd
import re

#this isn't really data preprocessing i just combined all the csv's into one relevant one
#we will use this later when we start actually scraping reviews of games

#directory = r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files"

#csv_files = [f for f in os.listdir(directory) if f.startswith("checkpoint_page_") and f.endswith(".csv")]

#csv_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

#combined_df = pd.concat([pd.read_csv(os.path.join(directory, file)) for file in csv_files])

#combined_df.to_csv(os.path.join(directory, "metacritic_user_and_critic_reviews.csv"), index=False)

#df = pd.read_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV Files\good_critic_reviews.csv")

#df['Title'] = df['Title'].str.replace(r'^\s*\d{1,3},?\d{1,3}[.,]?\s*', '', regex=True)

#print(df['Title'].head(10))

#df.to_csv("cleaned_positive_critic_reviews.csv", index=False)

#import pandas as pd

# Load the file again
#df = pd.read_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files\cleaned_positive_user_reviews.csv")

# Clean the title column again (this handles numbers like "1. ", "1,000. ", etc.)
#df['Title'] = df['Title'].str.replace(r'^\s*\d{1,4}[,.]?\s*', '', regex=True)

# Confirm it's clean
#print(df['Title'].head(10))

# Save it again — this time truly cleaned
#df.to_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files\cleaned_positive_user_reviews.csv", index=False)

#
#
#
# #cleaning the reviews --------------------
# import pandas as pd
# import re
#
# #Load your dataset
# df = pd.read_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\scraped_negative_critic_reviews.csv")

#Clean the text
# def clean_text(text):
#    text = str(text).lower()  # lowercase
#    text = re.sub(r'\n|\r|\t', ' ', text)  # remove line breaks/tabs
#    text = re.sub(r'\\[a-z]', ' ', text)  # remove backslash escapes like \n \r
#    text = re.sub(r'\[.*?\]', '', text)  # remove brackets like [Jan 2009, p.71]
#    text = re.sub(r'http\S+', '', text)  # remove URLs
#    text = re.sub(r'[^a-z0-9\s]', '', text)  # remove punctuation except letters/numbers/spaces
#    text = re.sub(r'\s+', ' ', text)  # normalize whitespace
#    return text.strip()
#
# df['Cleaned_Words'] = df['Words'].apply(clean_text)
#
# #Add labels and source
# df['label'] = 1  # positive = 1, use 0 for negative datasets
# df['source'] = 'user'  # use 'critic' for critic datasets
#
# #Save cleaned version
# df[['Title', 'Cleaned_Words', 'label', 'source']].to_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files\final-critic.csv", index=False)

#import nltk
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
#nltk.download('stopwords')

# import pandas as pd
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.data import find
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
#
#
# # Check if punkt is available
# try:
#    find('tokenizers/punkt')
# except LookupError:
#    nltk.download('punkt')
#
# #Initialize lemmatizer and stop words
# lemmatizer = WordNetLemmatizer()
# stop_words = set(stopwords.words('english'))
#
# # Lemmatization + stop word removal
# def clean_and_lemmatize(text):
#    tokens = word_tokenize(str(text).lower())  # str() ensures we don't error on NaN
#    lemmatized = [lemmatizer.lemmatize(word) for word in tokens if word.isalpha() and word not in stop_words]
#    return ' '.join(lemmatized)
# #
# # Load your dataset
# mikumikubeammm =  pd.read_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files\final+user.csv")
#
#
# # Apply lemmatization
# mikumikubeammm['Lemmatized_Words'] = mikumikubeammm['Cleaned_Words'].apply(clean_and_lemmatize)
#
# # Overwrite Cleaned_Words with Lemmatized_Words
# mikumikubeammm['Cleaned_Words'] = mikumikubeammm['Lemmatized_Words']
#
# # Optionally drop the Lemmatized_Words column if you don't need it anymore
# mikumikubeammm.drop(columns=['Lemmatized_Words'], inplace=True)
#
# mikumikubeammm['source'] = 'user'
# mikumikubeammm['label'] = 1
#
#
# # Save the updated DataFrame to the same or new CSV file
# mikumikubeammm.to_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files\final+user.csv", index=False)
#
# print("✅ Cleaned_Words updated with lemmatized text and CSV saved.")
#
# # Preview results
# print(mikumikubeammm.head(5))
import re

# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
#
# # --- 1. Negation Handler ---
# def handle_negation(text):
#     negation_words = {"not", "no", "never", "n't"}
#     tokens = text.split()
#     new_tokens = []
#     skip = False
#
#     for i in range(len(tokens) - 1):
#         if tokens[i] in negation_words:
#             new_tokens.append(tokens[i] + '_' + tokens[i + 1])
#             skip = True
#         elif skip:
#             skip = False
#             continue
#         else:
#             new_tokens.append(tokens[i])
#
#     if not skip:
#         new_tokens.append(tokens[-1])
#
#     return ' '.join(new_tokens)
#
# # --- 2. Load CSV ---
# df = pd.read_csv("final-user.csv")
#
# # --- 3. Apply Negation Handler ---
# df['Negation_Handled'] = df['Cleaned_Words'].fillna("").apply(handle_negation)
#
# # --- 4. TF-IDF Vectorization ---
# vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000, stop_words='english')
# tfidf_matrix = vectorizer.fit_transform(df['Negation_Handled'])
#
# print("\nTF-IDF matrix shape:", tfidf_matrix.shape)
#
# # --- 5. Aggregate TF-IDF Scores Across All Reviews ---
# feature_names = vectorizer.get_feature_names()
# total_scores = tfidf_matrix.sum(axis=0).A1  # sum across all rows and flatten matrix
#
# term_scores = list(zip(feature_names, total_scores))
# top_terms = sorted(term_scores, key=lambda x: x[1], reverse=True)
#
# # --- 6. Show Top Terms Globally ---
# print("\nTop Global TF-IDF Terms:")
# for term, score in top_terms[:20]:
#     print(f"{term}: {score:.4f}")

# import pandas as pd
#
# def remove_duplicate_rows(csv_file_path, output_file_path=None):
#     # Load the CSV into a DataFrame
#     df = pd.read_csv(csv_file_path)
#
#     # Drop duplicate rows
#     df_no_duplicates = df.drop_duplicates()
#
#     # Save to a new CSV or overwrite the original
#     if output_file_path:
#         df_no_duplicates.to_csv(output_file_path, index=False)
#         print(f"Duplicates removed. Cleaned data saved to: {output_file_path}")
#     else:
#         df_no_duplicates.to_csv(csv_file_path, index=False)
#         print(f"Duplicates removed. Original file overwritten: {csv_file_path}")
#
# # Example usage
# csv_file = 'scraped_user_negative_reviews(hasproblems).csv'  # Replace with your actual file path
# # remove_duplicate_rows(csv_file)  # To overwrite original
# remove_duplicate_rows(csv_file, 'cleaned_file.csv')  # To save to new file

import pandas as pd
# import re
#
# def clean_title_column(csv_file_path, output_file_path=None):
#     # Load CSV
#     df = pd.read_csv(csv_file_path)
#
#     # Define a function to clean the title
#     def clean_title(title):
#         # Use regex to remove leading digits (with optional commas) ending in a dot
#         # Only removes if it's at the beginning of the string
#         return re.sub(r'^\s*\d{1,3}(?:,\d{3})*\.\s*', '', str(title))
#
#     # Apply cleaning function to 'Title' column
#     df['Title'] = df['Title'].apply(clean_title)
#
#     # Save the cleaned file
#     if output_file_path:
#         df.to_csv(output_file_path, index=False)
#         print(f"Cleaned titles saved to: {output_file_path}")
#     else:
#         df.to_csv(csv_file_path, index=False)
#         print(f"Cleaned titles saved to original file: {csv_file_path}")
#
# # Example usage
# csv_file = 'scraped_critic_negative_reviews_deduplicated.csv'  # Replace with your file name
# # clean_title_column(csv_file)  # Overwrite original
# clean_title_column(csv_file, 'preprocessed-critic.csv')  # Save to new file

# def drop_duplicate_reviews(csv_path, save_cleaned=True, output_path=None):
#     # Load the original CSV
#     df = pd.read_csv(csv_path)
#     print(f"🔢 Original row count: {len(df)}")
#
#     # Drop duplicates based on "Review Text" only
#     df_cleaned = df.drop_duplicates(subset=["Review Text"])
#     removed_count = len(df) - len(df_cleaned)
#     print(f"🧹 Removed {removed_count} duplicate review(s).")
#     print(f"✅ Cleaned row count: {len(df_cleaned)}")
#
#     # Optionally save to a new CSV
#     if save_cleaned:
#         if not output_path:
#             # Default to overwriting the original file (or modify if you want to avoid overwriting)
#             output_path = csv_path.replace(".csv", "_deduplicated.csv")
#         df_cleaned.to_csv(output_path, index=False)
#         print(f"💾 Cleaned data saved to: {output_path}")
#
#     return df_cleaned  # Return it in case you want to use it right away
#
# clean_df = drop_duplicate_reviews("scraped_critic_negative_reviews.csv")
#

import pandas as pd

# Load each CSV
user_pos = pd.read_csv("data/preprocessed+user.csv")
user_neg = pd.read_csv("data/preprocessed+critic.csv")
critic_pos = pd.read_csv("data/preprocessed-user.csv")
critic_neg = pd.read_csv("data/preprocessed-critic.csv")

# Optional: Check class sizes before combining
print("User Positive:", len(user_pos))
print("User Negative:", len(user_neg))
print("Critic Positive:", len(critic_pos))
print("Critic Negative:", len(critic_neg))

# Combine all into one big DataFrame
combined_df = pd.concat([user_pos, user_neg, critic_pos, critic_neg], ignore_index=True)

# Save if you want
combined_df.to_csv("game_reviews.csv", index=False)

print("✅ Combined dataset shape:", combined_df.shape)
