# Zscaler URL Management

This repository contains operational and informational scripts tailored for the Zscaler API. They facilitate the management and retrieval of data related to URL categories.

## Operational Scripts

These scripts provide functionalities to modify the URL categories.

### **add_urls_to_category.py**
- **Purpose:** Adds URLs from a CSV file to a user-specified category.
- **How to Use:** User specifies the desired category to add URLs to.

### **delete_url_from_all_categories.py**
- **Purpose:** Removes user-specified URLs from all categories they are associated with.
- **How to Use:** Provide the URLs to be removed in a CSV file.

## Informational Scripts

These scripts help in fetching data or validating configurations.

### **auth_validation.py**
- **Purpose:** Validates if the API credentials and CSV reading configurations are correct.
- **How to Use:** If validation fails, ensure that the credentials are correct or check the CSV file path.

### **lookup_category_contents.py**
- **Purpose:** Fetches detailed data about user-specified categories.
- **How to Use:** List the categories to be looked up in a CSV file.

### **lookup_url.py**
- **Purpose:** Provides detailed information about user-specified URLs.
- **How to Use:** List the URLs to be looked up in a CSV file.

---

## Getting Started

1. Clone the repository to your local machine.
2. Provide the necessary configurations like the API credentials and paths to the CSV files.
3. Run the desired script to manage or fetch data related to URL categories.
