#!/bin/bash
# Automated Database Backup Script for MyCRM
# Creates encrypted backups with retention policy

set -e  # Exit on error

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DB_HOST="${DATABASE_HOST:-db}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_NAME="${DATABASE_NAME:-mycrm_db}"
DB_USER="${DATABASE_USER:-postgres}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="mycrm_backup_${TIMESTAMP}.sql.gz"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY}"

echo "Starting database backup at $(date)"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Perform backup
echo "Creating backup: ${BACKUP_FILE}"
PGPASSWORD="${DATABASE_PASSWORD}" pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --format=plain \
    --no-owner \
    --no-acl \
    | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Encrypt backup if encryption key is provided
if [ -n "${ENCRYPTION_KEY}" ]; then
    echo "Encrypting backup..."
    openssl enc -aes-256-cbc \
        -salt \
        -in "${BACKUP_DIR}/${BACKUP_FILE}" \
        -out "${BACKUP_DIR}/${BACKUP_FILE}.enc" \
        -k "${ENCRYPTION_KEY}"
    
    # Remove unencrypted backup
    rm "${BACKUP_DIR}/${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE}.enc"
    echo "Backup encrypted: ${BACKUP_FILE}"
fi

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
echo "Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

# Upload to cloud storage (if configured)
if [ -n "${AWS_S3_BUCKET}" ]; then
    echo "Uploading to S3: ${AWS_S3_BUCKET}"
    aws s3 cp \
        "${BACKUP_DIR}/${BACKUP_FILE}" \
        "s3://${AWS_S3_BUCKET}/backups/${BACKUP_FILE}" \
        --storage-class STANDARD_IA
    echo "Backup uploaded to S3"
fi

if [ -n "${AZURE_STORAGE_ACCOUNT}" ]; then
    echo "Uploading to Azure Blob Storage"
    az storage blob upload \
        --account-name "${AZURE_STORAGE_ACCOUNT}" \
        --container-name backups \
        --name "${BACKUP_FILE}" \
        --file "${BACKUP_DIR}/${BACKUP_FILE}" \
        --auth-mode login
    echo "Backup uploaded to Azure"
fi

# Clean up old backups (retention policy)
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "mycrm_backup_*.sql.gz*" -mtime +${RETENTION_DAYS} -delete
echo "Old backups cleaned up"

# Verify backup integrity
if [ "${BACKUP_FILE##*.}" = "enc" ]; then
    # Verify encrypted backup can be decrypted
    openssl enc -aes-256-cbc -d \
        -in "${BACKUP_DIR}/${BACKUP_FILE}" \
        -k "${ENCRYPTION_KEY}" \
        | gzip -t 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✓ Backup integrity verified (encrypted)"
    else
        echo "✗ Backup integrity check failed!"
        exit 1
    fi
else
    # Verify plain backup
    gzip -t "${BACKUP_DIR}/${BACKUP_FILE}"
    if [ $? -eq 0 ]; then
        echo "✓ Backup integrity verified"
    else
        echo "✗ Backup integrity check failed!"
        exit 1
    fi
fi

# Send notification (if configured)
if [ -n "${SLACK_WEBHOOK_URL}" ]; then
    curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"✓ MyCRM backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})\"}"
fi

echo "Backup process completed successfully at $(date)"
echo "Backup location: ${BACKUP_DIR}/${BACKUP_FILE}"
