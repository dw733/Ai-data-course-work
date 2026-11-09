# Ontario Housing Price Prediction

A Durham College group project by Mohamed Barakat, Ahmed Barakat, Hasan Syed and Mahesh Tharu. The assignment compares Linear Regression, Ridge Regression and Random Forest using Ontario housing records and evaluates them with RMSE, MAE and R².

- [Coursework notebook](Ontario-Housing.ipynb)
- [Original coursework report](Original-Report.md)

The saved notebook ranked Linear Regression first by RMSE, while the original report names Random Forest as the best model. The notebook also uses a synthetic benchmark derived from the target price as a model input. That leaks the target into the prediction, so the archived scores should not be used as evidence of performance on new properties. An independent evaluation would exclude that feature and rerun model selection on a clean split.

The original dataset is needed to reproduce the analysis. The notebook export omits saved outputs containing listing-level records.
