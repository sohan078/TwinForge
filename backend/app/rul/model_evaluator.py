from __future__ import annotations

from math import sqrt
from xml.parsers.expat import model

import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


class RULModelEvaluator:
    @staticmethod
    def evaluate(model, X, y) -> dict[str, float]:
        predictions = model.predict(X)

        mae = mean_absolute_error(y, predictions)
        rmse = sqrt(mean_squared_error(y, predictions))
        r2 = r2_score(y, predictions)

        return {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
        }

    @staticmethod
    def evaluate_per_run(
        model,
        X: pd.DataFrame,
        y: pd.Series,
        run_ids: pd.Series,
    ) -> pd.DataFrame:
        predictions = model.predict(X)

        results = pd.DataFrame(
            {
                "run_id": run_ids.to_numpy(),
                "actual": y.to_numpy(),
                "predicted": predictions,
            }
        )

        rows = []

        for run_id, group in results.groupby("run_id"):
            mae = mean_absolute_error(
                group["actual"],
                group["predicted"],
            )

            rmse = sqrt(
                mean_squared_error(
                    group["actual"],
                    group["predicted"],
                )
            )

            rows.append(
                {
                    "run_id": run_id,
                    "mae": float(mae),
                    "rmse": float(rmse),
                }
            )

        return pd.DataFrame(rows)

    @staticmethod
    def evaluate_near_failure(
        model,
        X: pd.DataFrame,
        y: pd.Series,
        threshold_hours: float = 50.0,
    ) -> dict[str, float | int] | None:
        """
        Evaluate RUL prediction accuracy for samples
        approaching failure.

        Includes actual RUL values from 0 through threshold_hours.
        """

        if threshold_hours < 0:
            raise ValueError(
                "threshold_hours must be non-negative"
            )

        mask = (y >= 0) & (y <= threshold_hours)

        if not mask.any():
            return None

        X_near_failure = X.loc[mask]
        y_near_failure = y.loc[mask]

        predictions = model.predict(X_near_failure)

        return {
            "mae": float(
                mean_absolute_error(y_near_failure, predictions)
            ),
        "rmse": float(
            sqrt(
                mean_squared_error(
                    y_near_failure,
                    predictions,
                )
            )
        ),
        "sample_count": int(len(y_near_failure)),
    }