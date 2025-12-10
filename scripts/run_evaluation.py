"""Run evaluation for baseline and generated tests."""

from __future__ import annotations

from agent.evaluation import evaluate_suite, save_metrics
from agent.mutation import compute_mutation_score, DEFAULT_TARGET_MODULE, BASELINE_TESTS, GENERATED_TESTS, save_mutation_metrics


def main() -> None:
    # Baseline suite
    baseline_metrics = evaluate_suite("baseline", "tests/baseline/test_*_baseline.py")
    save_metrics(baseline_metrics, "data/results/eval_baseline.json")

    baseline_mut = compute_mutation_score("baseline", DEFAULT_TARGET_MODULE, BASELINE_TESTS)
    save_mutation_metrics(baseline_mut, "data/results/mutation_baseline.json")

    # Generated suite
    generated_metrics = evaluate_suite("generated", "tests/generated/test_*_generated.py")
    save_metrics(generated_metrics, "data/results/eval_generated.json")

    generated_mut = compute_mutation_score("generated", DEFAULT_TARGET_MODULE, GENERATED_TESTS)
    save_mutation_metrics(generated_mut, "data/results/mutation_generated.json")

    print("Saved baseline metrics to data/results/eval_baseline.json")
    print("Saved generated metrics to data/results/eval_generated.json")
    print("Saved mutation metrics to data/results/mutation_*.json")

if __name__ == "__main__":
    main()
