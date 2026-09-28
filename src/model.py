# %%
# Daten laden

from pathlib import Path
from tensorflow import keras


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "Data" / "Datasets" / "set_v001"
)

# this method can take folders and turn them into input (xs) and labels (xy)
# train_ds -> train dataset
# in train_ds sind die images und die labels enthalten man kann über sie drüber iterieren
# außerdem wird geshuffelt
# 0 = kein Angriff, 1 = Angriff
# 
def load_dataset(split, shuffle=False):
    return keras.utils.image_dataset_from_directory(
        DATA_DIR / split,
        class_names=["no_attack", "attack"],  # hier die namen der unterornder angebe
        label_mode="int",                     # zahlenformat hier 0 und 1
        color_mode="grayscale",               # farbe ja | nein?
        image_size=(515, 600),                # selbe größe wie images (Höhe, Breite)
        batch_size=None,                      # erst bei fit definieren
        shuffle=shuffle,                      # shuffeln
        seed=42,                              # seed für das shuffeln
    )

train_ds = load_dataset("train", shuffle=True)
val_ds = load_dataset("val")
test_ds = load_dataset("test")

# Shapes nach der Umwandlung in Arrays:
# train_images.shape → (1679, 515, 600, 1)
# train_labels.shape → (1679, 1)


# %% Daten als Arrays bereitstellen (einmal pro Sitzung ausführen)

import numpy as np

# Mit Arrays kann die Batchgröße später direkt in fit() angegeben werden.
def dataset_to_arrays(dataset):
    images = np.empty((len(dataset), 515, 600, 1), dtype=np.float32)
    labels = np.empty((len(dataset), 1), dtype=np.float32)
    for index, (image, label) in enumerate(dataset.as_numpy_iterator()):
        images[index] = image
        labels[index, 0] = label
    return images, labels


train_images, train_labels = dataset_to_arrays(train_ds)
val_images, val_labels = dataset_to_arrays(val_ds)
# test_ds bleibt für die abschließende Auswertung reserviert.


# %% Modell aufbauen

import tensorflow as tf

# vortrainiertes Netz in varibale "backbone" gespeichert
backbone = keras.applications.EfficientNetB0(
    weights="imagenet",  # imagenet hatt 1.000 klassen anders als die 10 CIFAR challenge
    include_top=False,   # Klassifikationskopf sind die letzen Layer des Netzes
    input_shape=(515, 600, 3), # meine bilder als input
)
backbone.trainable = False  

model = keras.Sequential([
    
    keras.Input(shape=(515, 600, 1)),

    # Den Grauwertkanal dreimal kopieren; Höhe und Breite bleiben erhalten.
    keras.layers.Lambda(
        lambda images: tf.image.grayscale_to_rgb(images),
        output_shape=(515, 600, 3),
        name="grayscale_to_rgb",
    ),

    backbone,


    keras.layers.GlobalAveragePooling2D(),
    keras.layers.Dense(1, activation="sigmoid"),
], name="elden_ring_attack")

model.summary()

# %% Training konfigurieren (nach dem Erstellen des Modells ausführen)

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=[
        keras.metrics.BinaryAccuracy(name="accuracy"),
        keras.metrics.Precision(name="precision"),
        keras.metrics.Recall(name="recall"),
    ],
)


# %% Training starten (erneutes Ausführen trainiert das Modell weiter)

history = model.fit(
    train_images,
    train_labels,
    validation_data=(val_images, val_labels),
    batch_size=8, 
    epochs=10,
    shuffle=True,
)

# %%
