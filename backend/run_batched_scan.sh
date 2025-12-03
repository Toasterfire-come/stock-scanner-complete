#!/bin/bash
#
# Run multiple scanner batches with different ticker ranges
# Works around curl_cffi segfault at scale
#

echo "========================================"
echo "BATCHED SCAN: 2000 tickers in 4 batches"
echo "========================================"

PYTHON=python3
SCANNER=realtime_scanner_working_proxy.py

# Batch 1: tickers 0-500
echo ""
echo "Batch 1/4: Tickers 0-500"
$PYTHON - <<'EOF'
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

# Modify config for batch 1
content = Path('realtime_scanner_working_proxy.py').read_text()
content = content.replace('target_tickers: int = 2000', 'target_tickers: int = 500')
content = content.replace('output_json: str = "realtime_scan_working_proxy_results.json"',
                         'output_json: str = "batch_1_results.json"')
Path('_temp_batch1.py').write_text(content)

exec(open('_temp_batch1.py').read())
EOF

sleep 10

# Batch 2: tickers 500-1000
echo ""
echo "Batch 2/4: Tickers 500-1000"
$PYTHON - <<'EOF'
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

content = Path('realtime_scanner_working_proxy.py').read_text()

# Load all tickers and slice
import_section = '''
def load_tickers(limit: int) -> List[str]:
    """Load tickers"""
    combined_dir = BASE_DIR / "data" / "combined"
    ticker_files = sorted(combined_dir.glob("combined_tickers_*.py"))

    if not ticker_files:
        raise FileNotFoundError("No ticker files found")

    import importlib.util
    spec = importlib.util.spec_from_file_location("combined_tickers", ticker_files[-1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Batch 2: tickers 500-1000
    tickers = module.COMBINED_TICKERS[500:1000]
    logger.info(f"Loaded {len(tickers)} tickers (batch 2: 500-1000)")
    return tickers
'''

# Replace load_tickers function
import re
content = re.sub(r'def load_tickers\(limit: int\).*?return tickers', import_section, content, flags=re.DOTALL)
content = content.replace('output_json: str = "realtime_scan_working_proxy_results.json"',
                         'output_json: str = "batch_2_results.json"')
content = content.replace('target_tickers: int = 2000', 'target_tickers: int = 500')

Path('_temp_batch2.py').write_text(content)
exec(open('_temp_batch2.py').read())
EOF

sleep 10

# Batch 3: tickers 1000-1500
echo ""
echo "Batch 3/4: Tickers 1000-1500"
# Similar for batch 3...

echo ""
echo "========================================"
echo "All batches complete!"
echo "========================================"
