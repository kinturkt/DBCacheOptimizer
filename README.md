# DBCacheOptimizer


## Overview
DBCacheOptimizer is a performance-driven system designed to optimize database queries by leveraging SQL and Redis caching. It enhances query efficiency by reducing response time and minimizing direct database hits, making it ideal for handling large datasets.

## Features
- **SQL Query Execution:** Retrieve data based on time range and other conditions.
- **Redis Caching:** Cache frequently accessed queries to improve performance.
- **Performance Comparison:** Measure and compare query execution time with and without caching.
- **Cloud Database Integration:** Connects to Azure SQL for real-world deployment.
- **Web-Based Interface:** User-friendly HTML interface for executing and monitoring queries.

## Technologies Used
- **Backend:** Flask (Python)
- **Database:** Azure SQL Server (via PyODBC)
- **Caching:** Redis
- **Frontend:** HTML, CSS
- **Logging:** Query execution times stored in `query_times.csv`

## Installation
### Prerequisites:
- Python 3.7+
- Redis server
- Flask
- pyodbc (for SQL database connection)
- Redis-py (for caching)

### Steps:
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/DBCacheOptimizer.git
   cd DBCacheOptimizer
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure database connection:**
   - Update the `connection()` function in `app.py` with your Azure SQL Server credentials.
5. **Run the application:**
   ```sh
   python app.py
   ```
6. **Access the Web UI:**
   Open `http://127.0.0.1:5000/` in your browser.

## File Structure
```
DBCacheOptimizer/
│── templates/
│   ├── index.html
│   ├── task_1.html
│   ├── task_1_redis.html
│   ├── task_11.html
│   ├── task_11_redis.html
│   ├── task_12.html
│   ├── task_12_redis.html
│── static/
│── app.py
│── requirements.txt
│── query_times.csv
│── README.md
```

## Future Enhancements
- **Visualization Dashboard:** Add real-time charts to track query performance.
- **Auto Cache Expiry Strategy:** Implement intelligent cache expiration policies.
- **Scalability Improvements:** Deploy on AWS/GCP for higher availability.

## Contributors
- **Kintur Shah**
