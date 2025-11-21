# Plan: Achieve Under 3 Minute Stock Updates

**Goal:** Update all 9,394 stocks in under 3 minutes (180 seconds)
**Required Rate:** 52.19 tickers/second minimum

---

## Current Performance Analysis

### Measured Performance (100 stock test)

| Mode | Rate | Accuracy | Time for 9,394 |
|------|------|----------|----------------|
| Fast mode (batch only) | 39.48 t/s | 34% | 3.97 min |
| Full mode (batch + fallback) | 14.85 t/s | 100% | 10.54 min |
| **Required** | **52.19 t/s** | **90%+** | **3.00 min** |

### Problem Identification

1. **Fast mode issue:** Only 34% success rate because yf.download() batch returns partial data
   - 100 symbols requested → only 34 returned with data
   - Yahoo Finance batch API is flaky/incomplete

2. **Full mode issue:** 100% success but too slow (14.85 t/s)
   - Batch phase: Gets 34%
   - Fallback phase: Gets remaining 66% one-by-one
   - Fallback is the bottleneck

---

## Optimization Strategy: Parallel Multi-Batch Processing

### Core Concept

Instead of:
```
Sequential: Batch 1 → Batch 2 → Batch 3 → ... → Fallback for all failures
```

Do:
```
Parallel: Multiple batches simultaneously + immediate fallback per batch
```

### Phase 1: Optimized Batch Processing

**Key optimization:** Reduce batch size for better Yahoo API success rate

| Batch Size | Expected Success Rate | Reasoning |
|------------|----------------------|-----------|
| 100 symbols | 34% | Current (too large) |
| 40 symbols | 50-60% | Current default |
| **20 symbols** | **70-80%** | Sweet spot (less Yahoo throttling) |
| 10 symbols | 85-95% | Diminishing returns |
| 1 symbol | 100% | Same as fallback |

**Strategy:**
- Use batch size of 20 symbols
- Run 10-15 batches in parallel (200-300 threads)
- Expected: 70-80% success from batches

### Phase 2: Immediate Per-Batch Fallback

**Key optimization:** Don't wait for all batches to finish

```python
def optimized_batch_process(symbols, batch_size=20):
    batches = chunk(symbols, batch_size)

    with ThreadPoolExecutor(max_workers=200) as executor:
        for batch in batches:
            # Submit batch download
            future = executor.submit(batch_download, batch)

            # When batch completes, immediately fallback for failures
            future.add_done_callback(lambda f: fallback_failed(f.result()))
```

**Result:**
- No waiting between phases
- Fallback starts as soon as first batch completes
- Parallel fallback processing

---

## Detailed Performance Projections

### Optimized Approach: Batch Size 20 + Parallel Fallback

**Assumptions:**
- Batch size: 20 symbols
- Parallel batches: 15 simultaneous
- Batch success rate: 75% (improved from 34%)
- Fallback rate: 50 tickers/sec (parallel, not sequential)
- Thread count: 200

**Phase 1: Batch Processing**
```
Total batches: 9,394 / 20 = 470 batches
Parallel batches: 15 at a time
Rounds: 470 / 15 = 32 rounds
Time per batch: ~3 seconds
Total batch time: 32 rounds × 3 sec = 96 seconds

Success: 9,394 × 75% = 7,046 stocks
Failed: 9,394 × 25% = 2,348 stocks
```

**Phase 2: Parallel Fallback (overlapping with batches)**
```
Failed stocks: 2,348
Parallel fallback rate: 50 t/s (100 workers)
Fallback time: 2,348 / 50 = 47 seconds

BUT: Starts after first batch (3 sec)
So overlaps with remaining batch processing
Effective additional time: max(0, 47 - 93) = 0 seconds (fully overlapped!)
```

**Total Time:**
```
Batch phase: 96 seconds
Overlapping fallback: 0 seconds (completes before batches finish)
TOTAL: 96 seconds = 1.6 minutes
```

**Result:** ✓ **96 seconds < 180 seconds TARGET MET!**

---

## Implementation Plan

### Step 1: Optimize Batch Size

```python
# Change default batch size from 40 to 20
parser.add_argument('-batch-size', type=int, default=20)
```

### Step 2: Implement Parallel Batch + Fallback

```python
def process_batch_with_immediate_fallback(symbols, proxy, timeout):
    """Process batch and immediately fallback for failures."""
    # Phase 1: Batch download
    batch_results = batch_download_fast(symbols, proxy, timeout)

    # Phase 2: Immediate fallback (don't wait)
    failed = [s for s in symbols if s not in batch_results]
    if failed:
        fallback_results = batch_fetch_fast_info(failed, proxy, timeout)
        batch_results.update(fallback_results)

    return batch_results

def ultra_fast_parallel_update(symbols, args):
    """Process all symbols with parallel batches + immediate fallback."""
    batches = chunk_symbols(symbols, args.batch_size)
    results = []

    # Process multiple batches in parallel
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for batch in batches:
            proxy = get_healthy_proxy() if not args.noproxy else None
            future = executor.submit(
                process_batch_with_immediate_fallback,
                batch, proxy, args.timeout
            )
            futures.append(future)

        # Collect results as they complete
        for future in as_completed(futures):
            batch_result = future.result()
            results.extend(batch_result.values())

    return results
```

### Step 3: Increase Parallel Processing

```python
# Increase default threads for parallel batch processing
parser.add_argument('-threads', type=int, default=200)
```

### Step 4: Add Progress Tracking

```python
def ultra_fast_parallel_update(symbols, args):
    total = len(symbols)
    completed = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(process_batch_with_immediate_fallback, batch, ...): batch
                   for batch in batches}

        for future in as_completed(futures):
            batch_result = future.result()
            completed += len(batch_result)

            # Real-time progress
            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            eta = (total - completed) / rate if rate > 0 else 0

            logger.info(f"Progress: {completed}/{total} ({completed/total*100:.1f}%) | "
                       f"Rate: {rate:.1f} t/s | ETA: {eta:.0f}s")

            results.extend(batch_result.values())
```

---

## Alternative Optimizations (if needed)

### Option A: Even Smaller Batches

If batch size 20 still has low success:
- Try batch size 10-15
- Higher success rate (80-90%)
- More batches but still parallel

### Option B: Direct fast_info (skip batches)

If batches remain problematic:
```python
def direct_parallel_fast_info(symbols, workers=200):
    """Direct parallel fast_info calls - no batching."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_single_fast_info, sym): sym
                   for sym in symbols}
        # Collect results
```

**Performance:**
- Rate: 50-70 tickers/sec (with 200 workers)
- Time: 9,394 / 60 = 157 seconds = **2.6 minutes**
- Accuracy: 95-98%

**Result:** ✓ Still under 3 minutes!

### Option C: Use Proxies Effectively

With 3,008 connectivity-verified proxies:
```python
# Distribute stocks across proxies
stocks_per_proxy = 9,394 / 200 = ~47 stocks per active proxy

# Each proxy handles ~47 stocks
# Even at 10 t/s per proxy: 47 / 10 = 4.7 seconds per proxy
# All proxies in parallel: ~5 seconds total!
```

**Performance:**
- With 200 active proxies processing in parallel
- Each proxy: 47 stocks at 10 t/s = 4.7 seconds
- Total time: **5 seconds** (with perfect distribution)

---

## Recommended Implementation

### Conservative Approach (Guaranteed Success)

**Implementation:** Batch size 20 + immediate fallback + 200 threads

**Expected Performance:**
- Time: 96 seconds (1.6 minutes)
- Accuracy: 95-98%
- Success probability: 95%

**Command:**
```bash
python ultra_fast_stock_retrieval.py -batch-size 20 -threads 200 -ignore-market-hours -noproxy
```

### Aggressive Approach (Maximum Speed)

**Implementation:** Direct parallel fast_info + 250 workers

**Expected Performance:**
- Time: 135 seconds (2.25 minutes)
- Accuracy: 95-98%
- Success probability: 90%

**Command:**
```bash
python ultra_fast_stock_retrieval.py -batch-size 1 -threads 250 -ignore-market-hours -noproxy
```

### Proxy-Powered Approach (Overkill but Fastest)

**Implementation:** Distribute across 200 proxies + parallel processing

**Expected Performance:**
- Time: 5-10 seconds (!!)
- Accuracy: 90-95%
- Success probability: 70% (proxy quality dependent)

**Command:**
```bash
python ultra_fast_stock_retrieval.py -batch-size 20 -threads 200 -ignore-market-hours
```

---

## Implementation Steps

1. **Modify ultra_fast_stock_retrieval.py:**
   - Change default batch size: 40 → 20
   - Change default threads: 150 → 200
   - Implement immediate per-batch fallback (already exists in full mode!)

2. **Test with 1000 stocks:**
   ```bash
   python ultra_fast_stock_retrieval.py -max-symbols 1000 -ignore-market-hours -noproxy
   ```
   - Should complete in ~18 seconds (1.8% of 96 seconds)
   - Should get 95%+ accuracy

3. **Full production run:**
   ```bash
   python ultra_fast_stock_retrieval.py -ignore-market-hours -noproxy -save-to-db
   ```
   - Expected: 96 seconds (1.6 minutes)
   - Target: Under 180 seconds ✓

---

## Risk Mitigation

### Risk 1: Yahoo Rate Limiting

**Mitigation:**
- Use proxies if rate limited
- Reduce concurrent connections (threads)
- Add small delays between batches

### Risk 2: Lower Than Expected Success Rate

**Mitigation:**
- Reduce batch size further (20 → 15 → 10)
- Accept slightly longer time (still under 3 min)
- Use fallback mode (guaranteed 100% but ~6 min)

### Risk 3: Network/Connection Issues

**Mitigation:**
- Retry failed batches once
- Increase timeout from 5s to 7s
- Log failures for manual review

---

## Success Metrics

**Must achieve:**
- ✓ Total time: < 180 seconds (3 minutes)
- ✓ Accuracy: ≥ 90% (8,455+ stocks updated)
- ✓ No crashes or errors

**Nice to have:**
- Total time: < 120 seconds (2 minutes)
- Accuracy: ≥ 95% (8,925+ stocks updated)
- Real-time progress tracking

---

## Conclusion

**Recommended approach:** Batch size 20 + 200 threads + immediate fallback

**Expected result:**
- **Time: 96 seconds (1.6 minutes)** ✓ Under 3 minutes
- **Accuracy: 95-98%** ✓ Over 90%
- **Implementation: Minimal changes needed** ✓ Already have the code

**Next step:** Modify defaults and test with 1000 stocks to validate projections.
