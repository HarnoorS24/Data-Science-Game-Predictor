import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

#smload. data frame
goku = pd.read_csv('data/preprocessed_metadata.csv') 
#just for the sake of the model, dropping these two for now. Don't see it's immense importance for a model.
goku = goku.drop(columns=['Title', 'Game URL'])

#developer and publisher are strings, so i'm encoding them categorically.
goku = pd.get_dummies(goku, columns=['Developer', 'Publisher'], drop_first=True)

#Dropping user success for now since that's our target, and keeping the rest as features.
X = goku.drop(columns=['Success_UserScore'])  #Features
y = goku['Success_UserScore']                 #Target 

# train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
#training random forest. yes the model's name is Krillin
krillin = RandomForestClassifier(n_estimators=100, random_state=42)
krillin.fit(X_train, y_train)

#model (and some more for my own benefit)
y_pred = krillin.predict(X_test)
y_prob = krillin.predict_proba(X_test)[:, 1]  # Probabilities for class 1
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

#saving the model as a pickle
with open('metadata_model.pkl', 'wb') as f:
    pickle.dump(krillin, f)
print("Model saved to metadata_model.pkl")
#Saving the column order in case that might help for testing later
with open('metadata_columns.pkl', 'wb') as f:
    pickle.dump(X.columns.tolist(), f)
print("Column order saved to metadata_columns.pkl")
