# Métriques d'évaluation pour le prédicteur de victoire

import numpy as np


# Part de prédictions correctes avec le seuil 0.5
def accuracy(y, p):
    return float(np.mean((p >= 0.5) == (y > 0.5)))


# Accuracy d'un prédicteur naïf qui prédit toujours la classe majoritaire du train
def baseline_accuracy(y_train, y_eval):
    majority = 1.0 if np.mean(y_train) >= 0.5 else 0.0
    return float(np.mean(y_eval == majority))


# Accuracy sur les top_fraction % de drafts où |p - 0.5| est le plus grand
def confident_accuracy(y, p, top_fraction=0.1):
    n_top = max(1, int(len(p) * top_fraction))
    top = np.argsort(np.abs(p - 0.5))[-n_top:]
    return accuracy(y[top], p[top])
