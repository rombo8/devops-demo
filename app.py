from flask import Flask
import psycopg2
import redis

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="devops_demo",
        user="devops",
        password="devops_password",
    )


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


@app.route("/")
def hello():
    cached_count = redis_client.get("visits_count")

    if cached_count is not None:
        return f"Hello from DevOps Demo! You are visitor #{cached_count} (from Redis cache)"

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT count FROM visits WHERE id = 1"
    )

    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    redis_client.set("visits_count", count)

    return f"Hello from DevOps Demo! You are visitor #{count} (from PostgreSQL)"


@app.route("/visit")
def visit():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE visits SET count = count + 1 WHERE id = 1"
    )

    connection.commit()

    cursor.execute(
        "SELECT count FROM visits WHERE id = 1"
    )

    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    redis_client.set("visits_count", count)

    return f"Visitor count updated to {count}"


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)