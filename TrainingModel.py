import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
from tensorflow.keras.callbacks import Callback


mikumikubeam = pd.read_csv('game_reviews.csv')

#quite similar to what we did in lab 4
#followed similar naming strucutre to make it less confusing
X_train, X_test, y_train, y_test = train_test_split(
    mikumikubeam['Review Text'], mikumikubeam['+/-'], test_size=0.2, shuffle=True, stratify=mikumikubeam['+/-'], random_state=42
)


#tokenizer
#50000 should be enough right?
mikuToken = Tokenizer(num_words=50000, oov_token="<OOV>")
mikuToken.fit_on_texts(X_train)

X_train_seq = mikuToken.texts_to_sequences(X_train)
X_test_seq = mikuToken.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=200, padding='post', truncating='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=200, padding='post', truncating='post')

#had to change the weights of negative reviews, mostly because the ratio of postiive to negative reviews was so big
#this apparently uses a formula to auto compute a valid weight
weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
mikuWeights = dict(enumerate(weights))
print(f"Weights used: {mikuWeights}")


#display of performance of model
class PerformanceReport(Callback):
    def on_epoch_end(self, epoch, logs=None):
        val_pred = (self.model.predict(X_test_pad) > 0.5).astype("int32").flatten()
        report = classification_report(y_test, val_pred, output_dict=True, zero_division=0)
        print(f"Epoch {epoch+1} Metrics:")
        print(f"  Precision: {report['1']['precision']:.4f}")
        print(f"  Recall:    {report['1']['recall']:.4f}")
        print(f"  F1-Score:  {report['1']['f1-score']:.4f}\n")


model = Sequential([
    Embedding(input_dim=50000, output_dim=64, input_length=200), GlobalAveragePooling1D(),
    Dense(32, activation='relu'), Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])



#actually training the model
model.fit(
    X_train_pad,
    y_train,
    #tried running more epochs, but it simply took too long
    epochs=5,
    validation_data=(X_test_pad, y_test),
    class_weight=mikuWeights,
    callbacks=[PerformanceReport()]
)

print("\nFinal Evaluation:")
loss, accuracy = model.evaluate(X_test_pad, y_test)
print(f"Accuracy: {accuracy:.4f}")


#prediction report
pred_probs = model.predict(X_test_pad)
pred_labels = (pred_probs > 0.5).astype("int32").flatten()

print("\nClassification Report:")
print(classification_report(y_test, pred_labels, zero_division=0))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, pred_labels))



#needed help especially for this part
#like what the hell is pickle
# === SAVE THE MODEL ===
model.save("sentiment_model.h5")

# === SAVE THE TOKENIZER ===
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(mikuToken, f)