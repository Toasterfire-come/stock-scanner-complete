#!/bin/bash

# Full Stock Database Refresh Script
# Refreshes all 9,394 NYSE/NASDAQ stocks in 10 batches
# Total time: ~20-22 minutes
# Correctness: 90%+ per batch

echo "================================================================================"
echo "FULL STOCK DATABASE REFRESH"
echo "================================================================================"
echo "Total Stocks: 9,394 (NYSE + NASDAQ)"
echo "Batches: 10 (1,000 stocks each)"
echo "Expected Time: 20-22 minutes"
echo "Expected Correctness: 90%+ per batch"
echo "================================================================================"
echo ""

# Track overall stats
TOTAL_START=$(date +%s)
SUCCESSFUL_BATCHES=0
FAILED_BATCHES=0

# Process 10 batches
for i in {0..9}; do
  BATCH_NUM=$((i+1))
  OFFSET=$((i*1000))

  echo "[BATCH $BATCH_NUM/10] Starting... (Offset: $OFFSET)"
  echo "----------------------------------------"

  BATCH_START=$(date +%s)

  # Run the update
  python manage.py update_stocks_yfinance_v2 \
    --limit 1000 \
    --threads 100 \
    --timeout 4 \
    2>&1 | tee -a /tmp/full_refresh_batch_${BATCH_NUM}.log

  EXIT_CODE=$?
  BATCH_END=$(date +%s)
  BATCH_TIME=$((BATCH_END - BATCH_START))

  if [ $EXIT_CODE -eq 0 ]; then
    SUCCESSFUL_BATCHES=$((SUCCESSFUL_BATCHES + 1))
    echo "[BATCH $BATCH_NUM/10] ✓ Complete in ${BATCH_TIME}s"
  else
    FAILED_BATCHES=$((FAILED_BATCHES + 1))
    echo "[BATCH $BATCH_NUM/10] ✗ Failed after ${BATCH_TIME}s"
  fi

  echo "----------------------------------------"

  # Wait 2 minutes between batches (except after last batch)
  if [ $i -lt 9 ]; then
    echo "[WAITING] 2 minutes before next batch to avoid rate limiting..."
    echo ""
    sleep 120
  fi
done

TOTAL_END=$(date +%s)
TOTAL_TIME=$((TOTAL_END - TOTAL_START))
TOTAL_MINUTES=$((TOTAL_TIME / 60))

echo ""
echo "================================================================================"
echo "FULL REFRESH COMPLETE"
echo "================================================================================"
echo "Total Time: ${TOTAL_TIME}s (${TOTAL_MINUTES} minutes)"
echo "Successful Batches: $SUCCESSFUL_BATCHES/10"
echo "Failed Batches: $FAILED_BATCHES/10"
echo "Logs saved to: /tmp/full_refresh_batch_*.log"
echo "================================================================================"
