import pandas as pd
import numpy as np
import pickle

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
vegeta = pd.DataFrame([manual_input])

#add any missing columns as 0, aka it isn't selected
for col in expected_columns:
    if col not in vegeta.columns:
        vegeta[col] = 0

#making sure column order is correct
vegeta = vegeta[expected_columns]

#PREDICTION :D やた！
prob = model.predict_proba(vegeta)[0][1]
prediction = "SUCCESSFUL" if prob >= 0.5 else "UNSUCCESSFUL"
confidence = f"{prob:.2%}" if prob >= 0.5 else f"{(1 - prob):.2%}"
print(f"\nPrediction: {prediction}")
print(f"Confidence: {confidence}")
