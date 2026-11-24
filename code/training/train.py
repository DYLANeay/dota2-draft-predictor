# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy>=2"]
# ///
# Run from code/: uv run training/train.py
#
# Entraîne la régression logistique sur data/processed/matches.csv (toutes les lignes)
# et sauve les poids dans code/doracle/data/model_weights.json,
# les métriques dans data/processed/model_metrics.json

import json
from pathlib import Path

from data import encode_drafts, load_matches, split_data
from logreg import fit, log_loss, predict_proba
from metrics import accuracy, baseline_accuracy, confident_accuracy

REPO_ROOT = Path(__file__).resolve().parents[2]
HEROES_JSON_PATH = REPO_ROOT / "code" / "doracle" / "data" / "heroes.json"
WEIGHTS_PATH = REPO_ROOT / "code" / "doracle" / "data" / "model_weights.json"
CSV_PATH = REPO_ROOT / "data" / "processed" / "matches.csv"
METRICS_PATH = REPO_ROOT / "data" / "processed" / "model_metrics.json"

SEED = 42
LEARNING_RATE = 0.05
EPOCHS = 5
BATCH_SIZE = 1024

HYPERPARAMS = {
    "seed": SEED,
    "learning_rate": LEARNING_RATE,
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
}


# Calcule les métriques d'un split : accuracy, log-loss, baseline, confident
def evaluate(y_train, y_eval, p_eval):
    return {
        "accuracy": accuracy(y_eval, p_eval),
        "log_loss": log_loss(y_eval, p_eval),
        "baseline_accuracy": baseline_accuracy(y_train, y_eval),
        "confident_accuracy": confident_accuracy(y_eval, p_eval),
    }


# Charge les données, entraîne le modèle, évalue puis sauve poids et métriques
def main():
    heroes = json.loads(HEROES_JSON_PATH.read_text())
    n_features = max(hero["id"] for hero in heroes) + 1
    print(f"n_features: {n_features} (max hero id + 1)")

    draft_heroes, y = load_matches(CSV_PATH)
    print(f"matches: {len(y)}")
    X = encode_drafts(draft_heroes, n_features)
    X_train, y_train, X_val, y_val, X_test, y_test = split_data(X, y, SEED)
    print(f"split: train {len(y_train)}, val {len(y_val)}, test {len(y_test)}")

    w, b = fit(X_train, y_train, LEARNING_RATE, EPOCHS, BATCH_SIZE, SEED)

    train_metrics = evaluate(y_train, y_train, predict_proba(X_train, w, b))
    val_metrics = evaluate(y_train, y_val, predict_proba(X_val, w, b))
    print(f"train metrics: {train_metrics}")
    print(f"val metrics:   {val_metrics}")

    # Le jeu de test n'est évalué qu'une seule fois, tout à la fin
    test_metrics = evaluate(y_train, y_test, predict_proba(X_test, w, b))
    print(f"test metrics:  {test_metrics}")

    weights = {
        "n_features": n_features,
        "bias": float(b),
        "weights": [float(value) for value in w],
        "hyperparams": HYPERPARAMS,
    }
    WEIGHTS_PATH.write_text(json.dumps(weights, indent=2) + "\n")

    metrics_report = {
        "n_features": n_features,
        "hyperparams": HYPERPARAMS,
        "split_sizes": {"train": len(y_train), "val": len(y_val), "test": len(y_test)},
        "train": train_metrics,
        "val": val_metrics,
        "test": test_metrics,
    }
    METRICS_PATH.write_text(json.dumps(metrics_report, indent=2) + "\n")

    print(f"[OK] {WEIGHTS_PATH}")
    print(f"[OK] {METRICS_PATH}")
    print(
        f"\nval accuracy {val_metrics['accuracy']:.4f} vs baseline "
        f"{val_metrics['baseline_accuracy']:.4f}"
    )
    print(
        f"test accuracy {test_metrics['accuracy']:.4f} vs baseline "
        f"{test_metrics['baseline_accuracy']:.4f}"
    )
    print(f"test confident accuracy (top 10%) {test_metrics['confident_accuracy']:.4f}")


if __name__ == "__main__":
    main()
