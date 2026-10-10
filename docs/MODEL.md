# Model and evaluation notes

[Back to README](../README.md)

## Data and preprocessing

The notebook reads a local `Fraud.csv`, which is excluded by `.gitignore`. Its saved output records 6,362,620 rows: 6,354,407 non-fraud transactions and 8,213 fraud transactions. The original dataset download URL and usage terms are not recorded in this repository; obtain and document the original dataset before reproducing or redistributing it.

The target is `isFraud`. Account identifiers `nameOrig` and `nameDest` are dropped. Transaction type is label-encoded; balance differences are added. The split is stratified 80/20 with `random_state=42`. SMOTE is applied only to the training partition, followed by a 200-tree Random Forest (`max_depth=15`, `min_samples_split=5`, `min_samples_leaf=2`).

## What the saved results mean

The saved classification report shows fraud precision 0.32, recall 0.98 and F1 0.48 on 1,643 positive test examples. The model identifies most fraud examples at the recorded decision threshold, but many positive alerts are false positives. Class imbalance makes overall accuracy alone an incomplete summary.

The notebook's recorded ROC-AUC uses `roc_auc_score(y_test, y_pred)` with hard labels. For ranking performance across thresholds, recompute it from `rf.predict_proba(X_test)[:, 1]`. Do not present the existing hard-label result as a probability-based benchmark.

## Reproduce the notebook

In a separate training environment, install pandas, NumPy, Matplotlib, Seaborn, scikit-learn, imbalanced-learn, joblib and Jupyter. Put the original `Fraud.csv` beside the notebook and run cells in order. Full-data oversampling and training can require substantial RAM; a smaller sample is suitable for a smoke check but does not reproduce the saved metrics. Record dependency versions, input data hash and machine details with any new result.

## Evaluation roadmap

1. Compare a simple baseline, class-weighted training and the current SMOTE pipeline.
2. Investigate category-aware sampling for the encoded transaction type.
3. Report PR-AUC, confusion matrices and precision/recall at selected thresholds.
4. Evaluate an appropriate time-based holdout and identify features available at prediction time. New balances are post-transaction information.
5. Assess calibration before interpreting model scores as real-world risk probabilities.

Documentation reflects the committed notebook; this documentation refresh did not retrain or change the model.
