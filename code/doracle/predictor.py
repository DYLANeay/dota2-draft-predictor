"""Win prediction: logistic regression on the hero draft."""

import json
import math
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_PATH = os.path.join(package_directory, "data", "model_weights.json")


# Prédicteur de victoire par régression logistique entraînée hors ligne
# weights est indexé par hero_id, un héros absent du draft compte 0
class WinPredictor:
    # Garde les poids du modèle (index = hero_id) et le biais appris
    def __init__(self, weights, bias):
        self.weights = weights
        self.bias = bias

    # Probabilité que Radiant gagne : sigmoid(forces Radiant - forces Dire + biais)
    def predict(self, radiant, dire):
        z = self.bias
        for hero_id in radiant:
            z += self.weights[int(hero_id)]
        for hero_id in dire:
            z -= self.weights[int(hero_id)]

        return 1.0 / (1.0 + math.exp(-z))

    # Charge les poids depuis le JSON écrit par l'entraînement
    @staticmethod
    def load(path):
        with open(path) as fp:
            data = json.load(fp)

        return WinPredictor(data["weights"], data["bias"])
