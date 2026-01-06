#!/bin/bash
# Database Restore Script for MyCRM
# Restores database from backup file

set -e  # Exit on error

# Configuration
BACKUP_FILE="$1"
DB_HOST="${DATABASE_HOST:-db}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_NAME="${DATABASE_NAME:-mycrm_db}"
DB_USER="${DATABASE_USER:-postgres}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"

if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /backup/mycrm_backup_20260102_120000.sql.gz"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "⚠️  WARNING: This will overwrite the current database!"
echo "Database: ${DB_NAME}"
echo "Backup file: ${BACKUP_FILE}"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Starting database restore at $(date)"

# Create temporary directory for restore
TEMP_DIR=$(mktemp -d)
RESTORE_FILE="${TEMP_DIR}/restore.sql"

# Decrypt if needed
if [ "${BACKUP_FILE##*.}" = "enc" ]; then
    if [ -z "${ENCRYPTION_KEY}" ]; then
        echo "Error: Backup is encrypted but BACKUP_ENCRYPTION_KEY is not set"
        exit 1
    fi
    
    echo "Decrypting backup..."
    openssl enc -aes-256-cbc -d \
        -in "${BACKUP_FILE}" \
        -out "${TEMP_DIR}/backup.sql.gz" \
        -k "${ENCRYPTION_KEY}"
    
    gunzip -c "${TEMP_DIR}/backup.sql.gz" > "${RESTORE_FILE}"
else
    gunzip -c "${BACKUP_FILE}" > "${RESTORE_FILE}"
fi

# Verify SQL file
if [ ! -s "${RESTORE_FILE}" ]; then
    echo "Error: Decompressed backup file is empty"
    rm -rf "${TEMP_DIR}"
    exit 1
fi

echo "Backup file prepared for restore"

# Drop existing connections to database
echo "Terminating existing database connections..."
PGPASSWORD="${DATABASE_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" \
    > /dev/null 2>&1 || true

# Drop and recreate database
echo "Recreating database..."
PGPASSWORD="${DATABASE_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS ${DB_NAME};" \
    -c "CREATE DATABASE ${DB_NAME};"

# Restore database
echo "Restoring database from backup..."
PGPASSWORD="${DATABASE_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -f "${RESTORE_FILE}" \
    --quiet

# Clean up
rm -rf "${TEMP_DIR}"

echo "✓ Database restore completed successfully at $(date)"
echo ""
echo "Next steps:"
echo "1. Run Django migrations: python manage.py migrate"
echo "2. Verify data integrity"
echo "3. Restart application services"

# Send notification (if configured)
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"⚠️ MyCRM database restored from: ${BACKUP_FILE}\"}"
fi
