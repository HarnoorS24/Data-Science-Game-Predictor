import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

#NLP based model.
#loading the model
sentiment_model = load_model("sentiment_model.h5")

#loading the tokenizer
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

MAX_LEN = 200
# review input
review = "This game looks ass."

#sentiment prediction
def get_nlp_score(text):
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post', truncating='post')
    prob = sentiment_model.predict(padded)[0][0]
    return prob  #returns a float between 0 and 1

nlp_prob = get_nlp_score(review)

#random forest model for Metadata ----------------------------------------------------------------

#loading the model we made. Self explanatory, but adding this because it's new for me
with open('metadata_model.pkl', 'rb') as f:
    model = pickle.load(f)
#adding the columns we saved, for the one hot encoding stuff later on
with open('metadata_columns.pkl', 'rb') as f:
    expected_columns = pickle.load(f)

#manual inputs that are just numbers. Is_AAA is boolean so that's 1 or 0 and thus i can put it here
manual_input = {
    'Release Year': 2024,
    'Platform Count': 2,
    'Is_AAA': 1
}

#these are also manual inputs, but they're gonna need a bit more work done since it needs to be one-hot encoded
publisher = "Sony Interactive Entertainment"
developer = "Firewalk Studios"
esrb = "ESRB_Rated T for Teen"
genres = ["Genre_Action", "Genre_Shooter"]
platforms = ["Platform_PlayStation", "Platform_PC"]
#this is gonna be the one hot encoding
#we'll set 1 for selected, 0 for all others (and have it default to 0)
for col in expected_columns:
    if "Publisher_" in col and publisher in col:
        manual_input[col] = 1
    elif "Developer_" in col and developer in col:
        manual_input[col] = 1
    elif "ESRB_Rated" in col:
        manual_input[col] = int(col == esrb)
    elif "Genre_" in col:
        manual_input[col] = int(col in genres)
    elif "Platform_" in col:
        manual_input[col] = int(col in platforms)

#input vector. I wanted some goofy names but i can only do so much when working with new concepts
#OK SO I LOWKEY JUST REALIZED THAT TAKING FROM BOTH MODELS MEANS VEGETA IS THE ONLY GOOFY NAME LMAOOO
vegeta = pd.DataFrame([manual_input]) 

#add any missing columns as 0, aka it isn't selected
for col in expected_columns:
    if col not in vegeta.columns:
        vegeta[col] = 0

#making sure column order is correct
vegeta = vegeta[expected_columns]

#PREDICTION :D やた！
metadata_prob = model.predict_proba(vegeta)[0][1]

#ok, so we just got everything. Let's combine the two models
#Combined model ------------------------------------------------------------------------
#weights. can be changed (each up to 1.0 max. or well i mean nothing is stoping you from making it higher)
nlp_weight = 1.0
metadata_weight = 0.6

# scaled so total possible score is at most 1
final_score = (nlp_prob * nlp_weight / 2) + (metadata_prob * metadata_weight / 2)
final_prediction = "SUCCESSFUL" if final_score >= 0.5 else "UNSUCCESSFUL"

#final results
print("\n--- NLP MODEL ---")
print(f"Sentiment Score: {nlp_prob:.2%}")
print("\n--- METADATA MODEL ---")
print(f"Metadata Score: {metadata_prob:.2%}")
print("\n--- FINAL COMBINED PREDICTION ---")
print(f"Weighted Score: {final_score:.2%}")
print(f"Prediction: {final_prediction}")
