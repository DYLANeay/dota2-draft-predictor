# Régression logistique implémentée à la main en numpy, sans scikit-learn

import numpy as np


# Écrase z dans [-30, 30] puis applique 1 / (1 + exp(-z)), évite l'overflow
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))


# Probabilité de victoire Radiant pour chaque draft
# Entrée : X (n, n_features) int8 ou float32, sortie : p (n,)
def predict_proba(X, w, b):
    return sigmoid(X.astype(np.float32) @ w + b)


# Log-loss moyenne : -mean(y log p + (1 - y) log(1 - p)), p borné par epsilon
def log_loss(y, p):
    p = np.clip(p, 1e-7, 1.0 - 1e-7)
    return float(-np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))


# Une étape de descente de gradient sur un mini-batch
# Sortie : nouveaux (w, b) après la mise à jour
def gradient_step(X_batch, y_batch, w, b, lr):
    X_batch = X_batch.astype(np.float32)
    error = sigmoid(X_batch @ w + b) - y_batch
    grad_w = X_batch.T @ error / len(y_batch)
    grad_b = float(np.mean(error))
    return w - lr * grad_w, b - lr * grad_b


# Descente de gradient mini-batch sur tout le train
# Affiche le log-loss train (moyenne des batchs) à chaque epoch
def fit(X, y, lr, epochs, batch_size, seed):
    w = np.zeros(X.shape[1], dtype=np.float32)
    b = 0.0
    rng = np.random.default_rng(seed)
    for epoch in range(epochs):
        order = rng.permutation(len(X))
        losses = []
        for start in range(0, len(X), batch_size):
            batch = order[start : start + batch_size]
            X_batch, y_batch = X[batch], y[batch]
            w, b = gradient_step(X_batch, y_batch, w, b, lr)
            losses.append(log_loss(y_batch, predict_proba(X_batch, w, b)))
        print(f"epoch {epoch + 1}/{epochs}  train log-loss {np.mean(losses):.4f}")
    return w, b
