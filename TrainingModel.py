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

# === LOAD DATA ===
df = pd.read_csv('game_reviews.csv')  # Must have 'Review Text' and '+/-' columns

# === SPLIT DATA ===
X_train, X_test, y_train, y_test = train_test_split(
    df['Review Text'], df['+/-'], test_size=0.2, shuffle=True, stratify=df['+/-'], random_state=42
)

# === TOKENIZE ===
tokenizer = Tokenizer(num_words=50000, oov_token="<OOV>")
tokenizer.fit_on_texts(X_train)

X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq = tokenizer.texts_to_sequences(X_test)

X_train_pad = pad_sequences(X_train_seq, maxlen=200, padding='post', truncating='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=200, padding='post', truncating='post')

# === CLASS WEIGHTS ===
class_weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weights_dict = dict(enumerate(class_weights))
print(f"Class Weights: {class_weights_dict}")

# === CUSTOM METRIC CALLBACK ===
class MetricsCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        val_pred = (self.model.predict(X_test_pad) > 0.5).astype("int32").flatten()
        report = classification_report(y_test, val_pred, output_dict=True, zero_division=0)
        print(f"Epoch {epoch+1} Metrics:")
        print(f"  🔹 Precision: {report['1']['precision']:.4f}")
        print(f"  🔹 Recall:    {report['1']['recall']:.4f}")
        print(f"  🔹 F1-Score:  {report['1']['f1-score']:.4f}\n")

# === MODEL ===
model = Sequential([
    Embedding(input_dim=50000, output_dim=64, input_length=200),
    GlobalAveragePooling1D(),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')  # Binary classification
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# === TRAIN ===
model.fit(
    X_train_pad,
    y_train,
    epochs=5,
    validation_data=(X_test_pad, y_test),
    class_weight=class_weights_dict,
    callbacks=[MetricsCallback()]
)

# === FINAL EVALUATION ===
print("\nFinal Evaluation on Test Set:")
loss, accuracy = model.evaluate(X_test_pad, y_test)
print(f"Accuracy: {accuracy:.4f}")

# === PREDICTIONS ===
pred_probs = model.predict(X_test_pad)
pred_labels = (pred_probs > 0.5).astype("int32").flatten()

print("\nClassification Report:")
print(classification_report(y_test, pred_labels, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, pred_labels))

# === SAVE THE MODEL ===
model.save("sentiment_model.h5")
print("Model saved to sentiment_model.h5")

# === SAVE THE TOKENIZER ===
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
print("Tokenizer saved to tokenizer.pkl")
