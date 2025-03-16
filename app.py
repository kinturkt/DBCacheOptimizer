from flask import Flask, render_template, request, json
import pyodbc
import redis
import time
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def connection():
    server = "tcp:kintur.database.windows.net,1433"
    database = "kintur"
    username = "ketan"
    password = "kinturshah123@"
    driver = "{ODBC Driver 18 for SQL Server}"

    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    conn = pyodbc.connect(conn_str)
    return conn

def get_redis_conn():
    return redis.Redis(host="kintur.redis.cache.windows.net", port=6380,
                        password="09WTPfX1q15pkrj6cg5NgcMcwcNEXHyg2AzCaOYw9Rw=", ssl=True, decode_responses=True)

def log_query_times(sql_time, redis_time=None, table_creation_time=None):
    with open("query_times.csv", "a") as f:
        f.write(f"{sql_time},{redis_time},{table_creation_time}\n")

def measure_table_creation():
    conn = connection()
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS data1 (
        time DATETIME,
        latitude FLOAT,
        longitude FLOAT,
        depth FLOAT,
        mag FLOAT,
        net VARCHAR(50),
        id VARCHAR(50)
    )"""
    s_t = time.time()
    cursor.execute(create_table_query)
    conn.commit()
    table_creation_time = time.time() - s_t
    cursor.close()
    conn.close()
    log_query_times(None, None, table_creation_time)
    return table_creation_time

@app.route('/task_1', methods=['GET', 'POST'])
def task_1():
    if request.method == 'POST':
        min_pop = request.form['min_pop']
        max_pop = request.form['max_pop']
        
        conn = connection()
        cursor = conn.cursor()
        ktsql_query = "SELECT time,latitude,longitude,depth,mag,net,id FROM data1 WHERE time BETWEEN ? AND ?"
        
        s_t = time.time()
        cursor.execute(ktsql_query, (min_pop, max_pop))
        output = cursor.fetchall()
        tt_for_query = time.time() - s_t

        cursor.close()
        conn.close()
        log_query_times(tt_for_query)

        return render_template('task_1.html', output=output, tt_for_query=tt_for_query, data=1)
    
    return render_template('task_1.html')

@app.route('/task_1_redis', methods=['GET', 'POST'])
def task_1_redis():
    if request.method == 'POST':
        min_pop = request.form.get('min_pop')
        max_pop = request.form.get('max_pop')

        redis_conn = get_redis_conn()
        cache_key = f"{min_pop}:{max_pop}"
        cached_data = redis_conn.get(cache_key)

        if cached_data:
            results = json.loads(cached_data)
            return render_template('task_1_redis.html', output_3=results, from_cache=True, data=1)

        conn = connection()
        cursor = conn.cursor()
        query = "SELECT time, latitude, longitude, depth, mag, net, id FROM data1 WHERE time BETWEEN ? AND ?"
        s_t = time.time()
        cursor.execute(query, (min_pop, max_pop))
        output_3 = cursor.fetchall()
        tt_for_query_3 = time.time() - s_t

        cursor.close()
        conn.close()
        redis_conn.setex(cache_key, 3600, json.dumps(output_3))
        log_query_times(None, tt_for_query_3)

        return render_template('task_1_redis.html', output_3=output_3, tt_for_query_3=tt_for_query_3, from_cache=False, data=1)

    return render_template('task_1_redis.html')

@app.route('/task_11', methods=['GET', 'POST'])
def task_11():
    if request.method == 'POST':
        start_time = request.form.get('start_time')
        net_value = request.form.get('net_value')
        count = int(request.form.get('count'))

        conn = connection()
        cursor = conn.cursor()
        query = """
        SELECT TOP (?) time, latitude, longitude, depth, mag, net, id
        FROM data1
        WHERE net = ? AND time >= ?
        ORDER BY time
        """
        s_t = time.time()
        cursor.execute(query, (count, net_value, start_time))
        results = cursor.fetchall()
        e_t = time.time()
        tt_for_query = e_t - s_t

        cursor.close()
        conn.close()
        log_query_times(tt_for_query)

        return render_template('task_11.html', results=results, tt_for_query=tt_for_query, data=1)

    return render_template('task_11.html')


@app.route('/task_11_redis', methods=['GET', 'POST'])
def task_11_redis():
    if request.method == 'POST':
        start_time = request.form.get('start_time')
        net_value = request.form.get('net_value')
        count = int(request.form.get('count'))

        redis_conn = get_redis_conn()
        cache_key = f"task_11:{start_time}:{net_value}:{count}"
        cached_data = redis_conn.get(cache_key)

        if cached_data:
            results = json.loads(cached_data)
            return render_template('task_11_redis.html', results=results, from_cache=True, data=1)

        conn = connection()
        cursor = conn.cursor()
        query = """
        SELECT TOP (?) time, latitude, longitude, depth, mag, net, id
        FROM data1
        WHERE net = ? AND time >= ?
        ORDER BY time
        """
        s_t = time.time()
        cursor.execute(query, (count, net_value, start_time))
        results = cursor.fetchall()
        e_t = time.time()
        tt_for_query = e_t - s_t

        cursor.close()
        conn.close()
        redis_conn.setex(cache_key, 3600, json.dumps(results))
        log_query_times(tt_for_query)

        return render_template('task_11_redis.html', results=results, tt_for_query=tt_for_query, data=1)

    return render_template('task_11_redis.html')


@app.route('/task_12', methods=['GET', 'POST'])
def task_12():
    if request.method == 'POST':
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        net_value = request.form.get('net_value')
        count = int(request.form.get('count'))
        repetitions = int(request.form.get('repetitions'))

        results_list = []
        individual_times = []

        for _ in range(repetitions):
            conn = connection()
            cursor = conn.cursor()
            query = "SELECT TOP (?) time, latitude, longitude, depth, mag, net, id FROM data1 WHERE net = ? AND time BETWEEN ? AND ? ORDER BY time"
            s_t = time.time()
            cursor.execute(query, (count, net_value, start_time, end_time))
            results = cursor.fetchall()
            e_t = time.time()
            individual_times.append(e_t - s_t)
            cursor.close()
            conn.close()
            results_list.append(results)

        total_time = sum(individual_times)
        log_query_times(total_time)

        return render_template('task_12.html', results_list=results_list, individual_times=individual_times, total_time=total_time, data=1, repetitions=repetitions)

    return render_template('task_12.html')


@app.route('/task_12_redis', methods=['GET', 'POST'])
def task_12_redis():
    if request.method == 'POST':
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        net_value = request.form.get('net_value')
        count = int(request.form.get('count'))
        repetitions = int(request.form.get('repetitions'))

        redis_conn = get_redis_conn()
        cache_key = f"task_12:{start_time}:{end_time}:{net_value}:{count}:{repetitions}"
        cached_data = redis_conn.get(cache_key)

        if cached_data:
            cached_results = json.loads(cached_data)
            return render_template('task_12_redis.html', results_list=cached_results['results_list'], 
                                    individual_times=cached_results['individual_times'], 
                                    total_time=cached_results['total_time'], data=1, repetitions=repetitions)

        results_list = []
        individual_times = []

        for _ in range(repetitions):
            conn = connection()
            cursor = conn.cursor()
            query = "SELECT TOP (?) time, latitude, longitude, depth, mag, net, id FROM data1 WHERE net = ? AND time BETWEEN ? AND ? ORDER BY time"
            s_t = time.time()
            cursor.execute(query, (count, net_value, start_time, end_time))
            results = cursor.fetchall()
            e_t = time.time()
            individual_times.append(e_t - s_t)
            cursor.close()
            conn.close()
            results_list.append(results)

        total_time = sum(individual_times)
        redis_conn.setex(cache_key, 3600, json.dumps({"results_list": results_list, "individual_times": individual_times, "total_time": total_time}))
        log_query_times(total_time)

        return render_template('task_12_redis.html', results_list=results_list, individual_times=individual_times, total_time=total_time, data=1, repetitions=repetitions)

    return render_template('task_12_redis.html')

if __name__ == '__main__':
    app.run(debug=True)
