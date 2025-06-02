#!/bin/bash
set -e

# Split the comma-separated list into an array
IFS=',' read -ra DBS <<< "$POSTGRES_MULTIPLE_DATABASES"

for db in "${DBS[@]}"; do
    echo "Creating database if it doesn't exist: $db"
    db_exists=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$db'")
    if [ "$db_exists" != "1" ]; then
        createdb -U "$POSTGRES_USER" "$db"
    else
        echo "Database $db already exists, skipping."
    fi
done

# Optional: Create user `mlflow` and grant access
echo "Creating user mlflow if not exists"
user_exists=$(psql -U "$POSTGRES_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='mlflow'")
if [ "$user_exists" != "1" ]; then
    psql -U "$POSTGRES_USER" -c "CREATE USER mlflow WITH PASSWORD 'mlflow';"
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow;"
else
    echo "User mlflow already exists, skipping."
fi
