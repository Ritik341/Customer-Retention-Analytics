# Customer Engagement & Product Utilization Analytics for Customer Retention Strategy

## Project Overview
This project analyzes customer engagement, product utilization, and customer churn using Python, Pandas, and Streamlit. The objective is to understand customer retention patterns and identify factors associated with customer churn.

## Objectives
- Analyze the relationship between customer engagement and churn.
- Study how the number of products used relates to customer retention.
- Identify inactive and high-balance customers.
- Evaluate customer relationship strength.
- Support data-driven customer retention strategies.

## Dataset
The project uses a bank customer dataset containing 10,000 customer records and 14 columns.

Key fields include:
- CustomerId
- CreditScore
- Geography
- Gender
- Age
- Tenure
- Balance
- NumOfProducts
- HasCrCard
- IsActiveMember
- EstimatedSalary
- Exited

`Exited = 1` indicates churn, while `Exited = 0` indicates retention.

## Technologies Used
- Python
- Pandas
- Streamlit
- Excel
- GitHub

## Run the Project Locally

1. Clone this repository.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Run the Streamlit application:

   `streamlit run app.py`

## Project Structure
- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies
- `Customer Retention Data.csv` — Dataset

## Project Status
The project is under development. Dashboard analysis, testing, documentation, and deployment are being completed.
