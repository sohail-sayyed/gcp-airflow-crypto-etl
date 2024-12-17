# Google Cloud Airflow Data Pipeline for Trending Crypto Data

## 📝 Project Overview
This repository contains a **Google Cloud Platform (GCP)** data pipeline built with **Apache Airflow** to extract, transform, and load trending cryptocurrency data using the **Gecko Coins API**. The project leverages GCP services such as Cloud Storage and BigQuery to manage and process data efficiently.

---

## 📋 Workflow Description
The pipeline consists of the following Airflow Directed Acyclic Graphs (DAGs):

1. **Extract Trending Coins**  
   Fetches trending cryptocurrency data from the Gecko Coins API.

2. **Store Extracted Data in GCP Bucket**  
   Stores the raw JSON response in a GCP Cloud Storage bucket.

3. **Upload Raw Data to Raw Folder**  
   It saves the raw JSON data in the `raw/` folder in the GCP bucket.

4. **Data Transformation**  
   - Extracts specific fields and creates a structured data frame.  
   - Converts the `price_btc` and `market_cap` fields from **string** to **integer**.  
   - Converts the data frame into a CSV format.

5. **Upload Transformed Data**  
   Upload the transformed CSV data to the `transformed/` folder in the GCP bucket.

6. **Create BigQuery Dataset**  
   Creates a BigQuery dataset named `crypto_dataset`.

7. **Create BigQuery Table**  
   Creates a BigQuery table named `crypto_table` in the `crypto_dataset` with a defined schema.

8. **Upload Data to BigQuery Table**  
   Loads the transformed CSV data into the `crypto_table` in BigQuery.

---

## 🛠️ Tech Stack
- **Google Cloud Platform (GCP)**:
  - Cloud Storage
  - BigQuery
- **Apache Airflow**: Workflow orchestration
- **Python**: Core programming language
- **Gecko Coins API**: Data source for cryptocurrency information
- **Pandas**: For data manipulation and transformation

---

## 🏗️ Architecture Overview:

### Workflow Diagram

<p align="center">
  <img src="https://drive.google.com/uc?id=1wokfSMFmn_fQ27s_wEa8ih1o_cKYFzUi" alt="Architecture Diagram" style="border: 2px solid black; border-radius: 8px;" />
</p>

### Airflow DAG View:


![Airflow-ETL-Pipeline](https://drive.google.com/uc?export=view&id=1y5BX0i7snPqW9W02PxQVCfexMBt3RRtS)

## DAG Folder Structure in GCP:

![Airflow-ETL-Pipeline](https://drive.google.com/uc?export=view&id=1-udWoveiVnhH4y9ZorOYA-sG1UeH3S_V)


---


## 🚀 How It Works
1. **Step 1**: The first DAG extracts trending coins using the Gecko Coins API.  
2. **Step 2**: The second DAG stores the raw JSON data in the GCP bucket.  
3. **Step 3**: The third DAG organizes the raw data into the `raw/` folder.
               - ![GCP-Bucket-raw_folder-structure](https://drive.google.com/uc?export=view&id=1i1RRC6xeotxr26bYRtzGsqQG6MVDKQZ9)
4. **Step 4**: The fourth DAG:
   - Transforms the JSON data into a structured data frame.  
   - Changes schemas for `price_btc` and `market_cap` fields.  
   - Converts the data frame into a CSV format.  
5. **Step 5**: The fifth DAG uploads the CSV to the `transformed/` folder.
               - ![GCP-Bucket-transformed_folder-structure](https://drive.google.com/uc?export=view&id=1_GugMCdnSLl3npdwSr5EP_QHrxjQy1Xb)
6. **Step 6**: The sixth DAG creates the `crypto_dataset` in BigQuery.  
7. **Step 7**: The seventh DAG creates the `crypto_table` in BigQuery with a defined schema.
               - ![GCP-BigQuery-table-creation](https://drive.google.com/uc?export=view&id=1i1Obkx2t7brAlTl4RlqQqjnrkTXh-vhn)
8. **Step 8**: The final DAG uploads the transformed data from the CSV file into the BigQuery table.
               - ![GCP-bigquery-table-query](https://drive.google.com/uc?export=view&id=1Bhcl-u3RSpN5K7wiM1JxMKJjTUXj2mpT)

---

## 📋 BigQuery Schema
The BigQuery table `crypto_table` is created with the following schema:
- **id**: STRING  
- **name**: STRING  
- **symbol**: STRING  
- **price_btc**: INTEGER  
- **market_cap_usd**: INTEGER  

---

## ⚡ Getting Started

### Prerequisites
- Python 3.7+
- Google Cloud SDK installed and configured
- Airflow installed on a Google Cloud Composer or local setup
- Access to the Gecko Coins API

### 🌟 Features 
- Automated extraction and transformation of cryptocurrency data.
- Scalable storage using GCP Cloud Storage.
- Easy-to-query datasets via BigQuery.
- Fully orchestrated with Airflow for modular workflows.

### 📈 Future Enhancements
- Real-time streaming with Google Pub/Sub.
- Integration with data visualization tools like Google Data Studio.
- Support for additional data sources

### 🧍Author
Sohail Sayyed

- GitHub Profile: ["**Github**"](https://github.com/Sohail-09)
- LinkedIn: ["**LinkedIn**"](https://www.linkedin.com/in/sohailsayyed09/)
