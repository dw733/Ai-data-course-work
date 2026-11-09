> Archive of the course report. See [the project notes](README.md) for the issue found in the evaluation.

**Ontario Housing Price Prediction Using Regression Models**

**Introduction**

**The goal of this project was to build a machine learning model that could predict housing prices in Ontario using regression techniques. Another important part of the assignment was comparing the model’s predictions to a benchmark similar to the price estimate shown on the Zolo website.**

**To complete this project, I used an Ontario housing dataset and trained multiple regression models to see which one could predict prices most accurately. I evaluated the models using standard regression metrics such as RMSE, MAE, and R². I also checked whether the model predictions met the assignment thresholds, meaning whether they were within ±10% of the benchmark estimate and within ±15% of the actual housing price.**

**This project was useful because housing prices are influenced by many factors at the same time, and machine learning provides a practical way to analyze those relationships and make more accurate predictions.**

**Data Collection**

**For this project, I used the file data_on.csv, which contains Ontario housing listing data. The dataset includes a very large number of columns, but the main fields that were useful for this project were the property price, number of bedrooms, number of bathrooms, square footage, and location-based variables such as latitude and longitude.**

**I chose this dataset because it directly matches the assignment topic, which is predicting housing prices in Ontario. Using an Ontario-specific dataset made the project more relevant and realistic than using a general housing dataset from another place.**

**One limitation of the dataset was that it did not include a direct Zolo estimate column. Because of that, I created a benchmark estimate in the notebook called zolo_estimate. This allowed me to still evaluate the model using the same type of accuracy thresholds required in the assignment.**



**Data Preparation**

**Before building the models, the dataset had to be cleaned and prepared. The first step was standardizing the column names by converting them to lowercase. This made the notebook easier to work with and helped avoid errors caused by inconsistent column formatting.**

**Next, the important fields were converted into numeric form. Some values such as price, square footage, and property features were originally stored as text or contained extra symbols, so they had to be cleaned before they could be used in modeling.**

**After that, I selected the most relevant variables and removed rows with missing values in those fields. I did not use every column in the dataset because many of them were text-heavy, inconsistent, or unrelated to the main modeling goal. Instead, I focused on the strongest numeric housing variables so the project would stay clean, understandable, and executable.**

**This preparation stage was important because machine learning models rely on structured numeric data, and poor preprocessing would have reduced the quality of the results.**



**Feature Selection and Engineering**

**The main features I used were:**

- **property-beds**

- **property-baths**

- **property-sqft**

- **latitude**

- **longitude**

**These features were selected because they are some of the most important factors that affect house prices. In general, larger homes with more bedrooms and bathrooms tend to cost more, and location also plays a major role in housing value.**

**To strengthen the model, I also created a few new features:**

- **total_rooms = bedrooms + bathrooms**

- **bath_per_bed = bathrooms divided by bedrooms**

- **sqft_per_bed = square footage divided by bedrooms**

**These engineered features helped the model capture more meaningful relationships in the data. For example, the number of bathrooms compared to bedrooms can reflect house quality or convenience, while square footage per bedroom gives more information than square footage alone.**

**Feature engineering improved the project because it gave the models more useful inputs than just the raw variables.**



**Statistical Significance Testing**

**To better understand the data, I looked at the relationships between the selected features and price. A correlation analysis was useful here because it helped show which variables were most closely connected to housing price.**

**I expected variables like square footage, bedrooms, and bathrooms to have a positive relationship with price, and this was supported by the analysis. Location-related variables such as latitude and longitude were also important because they help represent the effect of where a property is located.**

**This part of the project matters because it shows that the features were not chosen randomly. Instead, they were selected based on both housing knowledge and measurable relationships in the dataset.**

**The statistical analysis also supported the decision to move forward with these features in the regression models.**

**Model Development**

**For this project, I trained three different regression models:**

- **Linear Regression**

- **Ridge Regression**

- **Random Forest Regressor**

**I used Linear Regression as a baseline model because it is simple and easy to interpret. Ridge Regression was included because it helps control overfitting and can perform better when predictors are somewhat related to each other. Random Forest was included because it can handle more complex and non-linear patterns in the data.**

**The dataset was split into training and testing sets so the models could be evaluated fairly. I also scaled the features for the linear models because scaling helps those models perform more consistently. Random Forest was trained on the non-scaled version of the data since tree-based models do not require scaling.**

**Using more than one model made the project stronger because it allowed me to compare simple and more advanced regression approaches instead of relying on only one method.**

**Model Evaluation and Accuracy Analysis**

**After training the models, I evaluated their performance using RMSE, MAE, and R².**

- **RMSE shows how large the prediction errors are overall**

- **MAE shows the average prediction error**

- **R² shows how much of the variation in housing price is explained by the model**

**In addition to these standard metrics, I also evaluated the models using the assignment thresholds:**

- **predictions within ±10% of the benchmark estimate**

- **predictions within ±15% of the actual price**

**Since the dataset did not include a real Zolo estimate, I used the simulated zolo_estimate benchmark created in the notebook. This allowed me to still compare the model against a benchmark estimate in a way that matched the assignment requirements.**

**Among the models, the Random Forest model performed the best overall. It was able to capture more complex relationships in the housing data, which helped it produce more accurate predictions than the linear models.**

**Once I ran the notebook, the final results table showed which model had the best combination of low error, high R², and strong threshold accuracy.**

**  
**

**Future Deployment Plan**

**If this project were turned into a real-world application, the model could be deployed as a housing price prediction tool for Ontario properties. A user could enter information such as number of bedrooms, bathrooms, square footage, and location, and the system could return a predicted price.**

**One possible way to deploy the model would be through a web application connected to a backend API. The trained model could be saved and loaded into a simple application built with Flask or FastAPI. The front end could then let users input property information and receive instant predictions.**

**To keep the model useful over time, it would need to be updated regularly with new housing data. This is especially important because the housing market changes often, and older training data may become less reliable.**

**In a more advanced version of the project, the simulated benchmark could be replaced with a real live benchmark source so the system could compare its predictions to current market estimates more directly.**

**Conclusion**

**Overall, this project showed that regression-based machine learning can be used to predict housing prices in Ontario with reasonable accuracy. Using data_on.csv, I cleaned the dataset, selected the most useful numeric features, engineered additional variables, and trained three different regression models.**

**The project also included evaluation based on both standard regression metrics and the assignment’s required threshold checks. This made the analysis more practical because it looked not only at general model error, but also at whether the predictions were close enough to be considered highly accurate.**

**Out of the models tested, Random Forest performed the best because it was better able to capture the more complex patterns in the housing data. Overall, the results show that machine learning can be a useful tool for housing price prediction when the data is prepared carefully and the model is evaluated properly.**
