# Chargement, encodage et découpage du dataset de drafts

import numpy as np


# Charge matches.csv : 10 hero_ids + radiant_win par ligne
# Sortie : heroes (n,10) int32, y (n,) float32 (1 = victoire Radiant)
def load_matches(csv_path):
    data = np.loadtxt(csv_path, delimiter=",", skiprows=1, dtype=np.int32)
    return data[:, :10], data[:, 10].astype(np.float32)


# Transforme les drafts en vecteurs : +1 héros Radiant, -1 héros Dire, 0 absent
# Entrée : heroes (n,10), sortie : matrice int8 (n, n_features)
def encode_drafts(heroes, n_features):
    n_rows = heroes.shape[0]
    X = np.zeros((n_rows, n_features), dtype=np.int8)
    rows = np.repeat(np.arange(n_rows), 5)
    # np.add.at gère les index répétés, contrairement à X[rows, cols] += 1
    np.add.at(X, (rows, heroes[:, :5].ravel()), 1)
    np.add.at(X, (rows, heroes[:, 5:].ravel()), -1)
    return X


# à la fin : on a un tableau de 2millions et 137 colonnes, chaque ligne est un draft encodé en
# vecteur de features, +1 pour les héros Radiant, -1 pour les héros Dire, 0 pour les héros absents


# Découpe en train/val/test 80/10/10 avec un mélange aléatoire reproductible
def split_data(X, y, seed):
    order = np.random.default_rng(seed).permutation(len(X))
    n_train = int(0.8 * len(X))
    n_val = int(0.1 * len(X))
    train, val, test = np.split(order, [n_train, n_train + n_val])
    return X[train], y[train], X[val], y[val], X[test], y[test]
