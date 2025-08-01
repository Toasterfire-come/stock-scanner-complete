"""
Django Management Command: Enhanced Stock Data Update using YFinance
Auto-scheduler every 5 minutes with NASDAQ-only focus and comprehensive data retrieval
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from stocks.models import Stock, StockPrice
import yfinance as yf
import logging
import time
import sys
from decimal import Decimal
import pandas as pd
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import schedule
from datetime import datetime, timedelta
import os
from pathlib import Path
import random
import requests
from proxy_manager import ProxyManager

# Add XAMPP MySQL to PATH if it exists
XAMPP_MYSQL_PATH = r"C:\xampp\mysql\bin"
if os.path.exists(XAMPP_MYSQL_PATH) and XAMPP_MYSQL_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + XAMPP_MYSQL_PATH
    print(f"INFO: Added XAMPP MySQL to PATH for stock updates: {XAMPP_MYSQL_PATH}")

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Enhanced stock data update with 5-minute auto-scheduler and NYSE focus'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='Comma-separated list of stock symbols to update'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Maximum number of stocks to update (default: 1000 for NYSE)'
        )
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Run scheduler mode (updates every 5 minutes continuously)'
        )
        parser.add_argument(
            '--startup',
            action='store_true',
            help='Run initial startup update then start scheduler'
        )
        parser.add_argument(
            '--nyse-only',
            action='store_true',
            default=True,
            help='Update only NYSE-listed tickers (default: True)'
        )
        parser.add_argument(
            '--threads',
            type=int,
            default=100,
            help='Number of concurrent threads (default: 100)'
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.01,
            help='Delay between requests in seconds (default: 0.01)'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode (display data without saving to database)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        parser.add_argument(
            '--no-proxy',
            action='store_true',
            help='Disable proxy usage (run without proxies)'
        )
        parser.add_argument(
            '--filter-delisted',
            action='store_true',
            help='Pre-filter delisted symbols before processing (faster processing)'
        )

    def handle(self, *args, **options):
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
            
        if options['startup']:
            self.stdout.write(self.style.SUCCESS("[RUN] STARTUP MODE: Running initial update then starting scheduler"))
            self._run_single_update(options)
            options['schedule'] = True
        
        if options['schedule']:
            self._run_scheduler(options)
        else:
            self._run_single_update(options)

    def _run_scheduler(self, options):
        """Run continuous scheduler every 5 minutes"""
        self.stdout.write(self.style.SUCCESS(" ENHANCED NYSE SCHEDULER STARTED"))
        self.stdout.write("=" * 70)
        self.stdout.write(" Schedule: Every 5 minutes")
        self.stdout.write("[TARGET] Target: NYSE tickers only")
        self.stdout.write(" Mode: Continuous updates")
        self.stdout.write(" Multithreading: Enabled")
        self.stdout.write(" Press Ctrl+C to stop the scheduler\n")

        # Schedule the job every 5 minutes
        schedule.every(5).minutes.do(self._run_single_update, options)
        
        # Show next run time
        next_run = schedule.next_run()
        self.stdout.write(f" Next update: {next_run.strftime('%H:%M:%S')}")

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n[STOP]  Scheduler stopped by user"))

    def _run_single_update(self, options):
        """Run a comprehensive single stock update"""
        
        start_time = time.time()
        
        # Display configuration
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("[UP] COMPREHENSIVE NYSE STOCK UPDATE"))
        self.stdout.write("="*70)
        self.stdout.write(f"[SETTINGS]  Threads: {options['threads']}")
        self.stdout.write(f"[TIME]  Delay per thread: {options['delay']}s")
        self.stdout.write(f"[TARGET] NYSE-only: {options['nyse_only']}")
        self.stdout.write(f"[STATS] Max stocks: {options['limit']}")
        self.stdout.write(f"[TEST] Test mode: {'ON' if options['test_mode'] else 'OFF'}")
        self.stdout.write(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get symbols to update
        if options['symbols']:
            symbols = [s.strip().upper() for s in options['symbols'].split(',')]
        else:
            symbols = self._get_nyse_symbols(options['limit'], options['nyse_only'])
        
        # Test yfinance connectivity
        connectivity_ok = self._test_yfinance_connectivity()
        if not connectivity_ok:
            self.stdout.write("[INFO] Proceeding with limited connectivity - individual requests may still work")
        self.stdout.flush()
        
        # Pre-filter delisted symbols if requested
        if options.get('filter_delisted', False):
            symbols = self._filter_delisted_symbols(symbols, sample_size=100)
        else:
            self.stdout.write(f"[INFO] Skipping delisted filtering - processing all {len(symbols)} symbols")
            self.stdout.flush()
        
        total_symbols = len(symbols)
        self.stdout.write(f"[UP] Processing {total_symbols} symbols")
        
        # Add immediate progress indicator
        self.stdout.write(f"[READY] Starting to process {total_symbols} symbols...")
        self.stdout.write(f"[FIRST] First 5 symbols: {', '.join(symbols[:5])}")
        self.stdout.flush()
        
        # Process the symbols
        results = self._process_stocks_batch(symbols, options['delay'], options['test_mode'], options['threads'], "NYSE UPDATE", options.get('no_proxy', False))
        
        # Calculate final duration
        results['duration'] = time.time() - start_time
        
        # Display final results
        self._display_final_results(results)
        
        # Check if interrupted
        if results.get('interrupted', False):
            self.stdout.write(self.style.WARNING(f"[INTERRUPTED] Script stopped by user after {results['duration']:.1f} seconds"))
            return
        
        # Schedule next run info if in scheduler mode
        if options.get('schedule'):
            next_run = schedule.next_run()
            if next_run:
                self.stdout.write(f" Next update: {next_run.strftime('%H:%M:%S')}")

    def _get_nyse_symbols(self, limit, nyse_only=True):
        """Get NYSE ticker symbols from otherlisted.txt data"""
        symbols = []
        
        if nyse_only:
            # Try to load NYSE tickers from the parsed data
            try:
                import json
                
                # Try NYSE stocks list first
                nyse_file = Path('nyse_stocks.json')
                if nyse_file.exists():
                    with open(nyse_file, 'r') as f:
                        data = json.load(f)
                        nyse_tickers = data.get('tickers', [])
                    
                    self.stdout.write(f"[STATS] NYSE-only mode: {len(nyse_tickers):,} NYSE tickers available")
                    
                    # Get existing stocks from database that are NYSE-listed
                    existing_stocks = Stock.objects.filter(
                        ticker__in=nyse_tickers,
                        exchange__iexact='NYSE'
                    ).values_list('ticker', flat=True)
                    
                    # Start with existing stocks
                    symbols.extend(list(existing_stocks))
                    
                    # Add missing NYSE tickers
                    missing_tickers = set(nyse_tickers) - set(symbols)
                    remaining_limit = limit - len(symbols)
                    symbols.extend(list(missing_tickers)[:remaining_limit])
                    
                    self.stdout.write(f"[SAVE] Found {len(existing_stocks)} existing NYSE stocks in database")
                    self.stdout.write(f"[UPDATE] Adding {min(len(missing_tickers), remaining_limit)} new NYSE tickers")
                    self.stdout.write(f"[TARGET] Processing {len(symbols)} NYSE stocks (limit: {limit})")
                    
                else:
                    # Fallback to major NYSE tickers
                    self.stdout.write(self.style.WARNING("[WARNING] NYSE list not found, using major NYSE tickers"))
                    
                    # Major NYSE tickers (top 100)
                    major_nyse = [
                        'A', 'AA', 'AACT', 'AAM', 'AAMI', 'AAP', 'AAT', 'AAUC', 'AB', 'ABBV', 'ABCB', 'ABEV', 'ABG', 'ABM', 'ABR', 'ABT', 'AC', 'ACA', 'ACCO', 'ACCS', 'ACEL', 'ACHR', 'ACI', 'ACM', 'ACN', 'ACP', 'ACR', 'ACRE', 'ACU', 'ACV', 'ACVA', 'ADC', 'ADCT', 'ADM', 'ADNT', 'ADT', 'ADX', 'AEE', 'AEF', 'AEFC', 'AEG', 'AEM', 'AEO', 'AEON', 'AER', 'AES', 'AESI', 'AFB', 'AFG', 'AFGB', 'AFGC', 'AFGD', 'AFGE', 'AG', 'AGCO', 'AGD', 'AGI', 'AGL', 'AGM', 'AGN', 'AGO', 'AGR', 'AGRO', 'AGS', 'AGX', 'AHH', 'AHL', 'AHT', 'AI', 'AIG', 'AIN', 'AIR', 'AIT', 'AJG', 'AJRD', 'AKA', 'AKO.A', 'AKO.B', 'AKR', 'AL', 'ALB', 'ALC', 'ALE', 'ALG', 'ALIT', 'ALK', 'ALL', 'ALLE', 'ALLY', 'ALSN', 'ALT', 'ALTG', 'ALV', 'ALX', 'AM', 'AMC', 'AME', 'AMG', 'AMH', 'AMK', 'AMN', 'AMP', 'AMR', 'AMT', 'AMX', 'AN', 'ANET', 'ANF', 'ANSS', 'ANTM', 'AON', 'AOS', 'APA', 'APD', 'APH', 'APLE', 'APO', 'APTV', 'AR', 'ARCH', 'ARCO', 'ARD', 'ARE', 'ARES', 'ARG', 'ARI', 'ARL', 'ARMK', 'ARNC', 'ARW', 'ASB', 'ASGN', 'ASH', 'ASIX', 'ASPN', 'ATCO', 'ATEN', 'ATGE', 'ATH', 'ATI', 'ATKR', 'ATO', 'ATR', 'ATSG', 'ATU', 'ATUS', 'ATVI', 'AVB', 'AVD', 'AVK', 'AVLR', 'AVNS', 'AVNT', 'AVT', 'AVY', 'AVYA', 'AWF', 'AWI', 'AWK', 'AWP', 'AWR', 'AX', 'AXL', 'AXP', 'AXR', 'AXS', 'AYI', 'AYX', 'AZEK', 'AZO', 'AZUL', 'BA', 'BABA', 'BAC', 'BAH', 'BAK', 'BALY', 'BAM', 'BANC', 'BAP', 'BAX', 'BB', 'BBD', 'BBDO', 'BBL', 'BBN', 'BBU', 'BBVA', 'BBW', 'BBY', 'BC', 'BCE', 'BCH', 'BCS', 'BDC', 'BDJ', 'BDN', 'BDX', 'BE', 'BEN', 'BF.A', 'BF.B', 'BFAM', 'BFS', 'BFZ', 'BG', 'BGB', 'BGH', 'BGR', 'BGS', 'BGT', 'BGX', 'BGY', 'BH', 'BHC', 'BHE', 'BHK', 'BHLB', 'BHP', 'BHV', 'BIF', 'BIG', 'BIO', 'BIP', 'BIT', 'BJ', 'BK', 'BKD', 'BKE', 'BKH', 'BKI', 'BKN', 'BKR', 'BKT', 'BLD', 'BLK', 'BLL', 'BLW', 'BLX', 'BMA', 'BME', 'BMEZ', 'BMI', 'BMO', 'BMY', 'BNED', 'BNS', 'BNY', 'BOE', 'BOH', 'BOX', 'BP', 'BPY', 'BR', 'BRBR', 'BRC', 'BRFS', 'BRK.A', 'BRK.B', 'BRO', 'BRT', 'BRX', 'BSAC', 'BSBR', 'BSL', 'BSM', 'BSMX', 'BST', 'BSTZ', 'BSX', 'BTI', 'BTO', 'BTT', 'BTU', 'BTZ', 'BUD', 'BUI', 'BURL', 'BV', 'BVN', 'BW', 'BWA', 'BWG', 'BWXT', 'BX', 'BXC', 'BXG', 'BXMT', 'BXMX', 'BXP', 'BXS', 'BYD', 'BYM', 'BZH', 'C', 'CAE', 'CAF', 'CAG', 'CAH', 'CAJ', 'CAL', 'CALX', 'CARR', 'CARS', 'CAT', 'CB', 'CBB', 'CBD', 'CBH', 'CBL', 'CBOE', 'CBRE', 'CBT', 'CBU', 'CBZ', 'CC', 'CCEP', 'CCH', 'CCI', 'CCJ', 'CCK', 'CCL', 'CCM', 'CCO', 'CCS', 'CCU', 'CCX', 'CCZ', 'CDAY', 'CDE', 'CDR', 'CE', 'CEA', 'CEE', 'CEIX', 'CELP', 'CEM', 'CEN', 'CEO', 'CEPU', 'CEQP', 'CF', 'CFG', 'CFR', 'CFX', 'CGA', 'CGC', 'CHA', 'CHCT', 'CHD', 'CHE', 'CHGG', 'CHH', 'CHK', 'CHL', 'CHPT', 'CHS', 'CHT', 'CHUY', 'CI', 'CIA', 'CIB', 'CIEN', 'CIG', 'CII', 'CIM', 'CINR', 'CIO', 'CIR', 'CIT', 'CKH', 'CL', 'CLB', 'CLDR', 'CLDT', 'CLF', 'CLGX', 'CLH', 'CLI', 'CLR', 'CLS', 'CLW', 'CLX', 'CMA', 'CMC', 'CMCM', 'CME', 'CMG', 'CMI', 'CMP', 'CMRE', 'CMS', 'CMU', 'CNA', 'CNC', 'CNHI', 'CNI', 'CNK', 'CNO', 'CNP', 'CNQ', 'CNR', 'CNS', 'CNX', 'CODI', 'COF', 'COG', 'COLD', 'COO', 'COP', 'COR', 'COTY', 'CP', 'CPA', 'CPB', 'CPE', 'CPF', 'CPG', 'CPK', 'CPLG', 'CPRI', 'CPS', 'CPSI', 'CPT', 'CR', 'CRC', 'CRD.A', 'CRD.B', 'CRH', 'CRI', 'CRK', 'CRL', 'CRM', 'CRS', 'CRT', 'CRY', 'CS', 'CSCO', 'CSL', 'CSV', 'CTA', 'CTB', 'CTBB', 'CTDD', 'CTL', 'CTLT', 'CTO', 'CTR', 'CTRA', 'CTS', 'CTSH', 'CTT', 'CTVA', 'CTY', 'CUB', 'CUBE', 'CUK', 'CULP', 'CURO', 'CUZ', 'CVA', 'CVBF', 'CVE', 'CVEO', 'CVG', 'CVI', 'CVNA', 'CVS', 'CVX', 'CW', 'CWEN', 'CWH', 'CWK', 'CWT', 'CX', 'CXE', 'CXH', 'CXO', 'CXP', 'CXW', 'CYD', 'CYH', 'CZZ', 'D', 'DAC', 'DAL', 'DAN', 'DAR', 'DAVA', 'DB', 'DBD', 'DBI', 'DBL', 'DCF', 'DCI', 'DCO', 'DCP', 'DCT', 'DD', 'DDD', 'DDS', 'DE', 'DEA', 'DECK', 'DEI', 'DELL', 'DEO', 'DESP', 'DFIN', 'DFS', 'DG', 'DGX', 'DHF', 'DHI', 'DHR', 'DHT', 'DHX', 'DIAX', 'DIN', 'DIS', 'DK', 'DKL', 'DKS', 'DLB', 'DLNG', 'DLR', 'DLX', 'DM', 'DMO', 'DNB', 'DNOW', 'DNZ', 'DO', 'DOC', 'DOCU', 'DOOR', 'DOV', 'DOW', 'DPG', 'DPZ', 'DQ', 'DRD', 'DRH', 'DRI', 'DRQ', 'DS', 'DSL', 'DSM', 'DSU', 'DSX', 'DT', 'DTE', 'DTF', 'DUK', 'DUKB', 'DV', 'DVN', 'DWIN', 'DX', 'DXB', 'DY', 'E', 'EAF', 'EAI', 'EARN', 'EAT', 'EB', 'EBF', 'EBR', 'EBS', 'EC', 'ECC', 'ECL', 'ECOM', 'ED', 'EDF', 'EDI', 'EDN', 'EDU', 'EE', 'EEA', 'EEX', 'EFC', 'EFR', 'EFT', 'EFX', 'EG', 'EGP', 'EGY', 'EHC', 'EIC', 'EIX', 'EL', 'EME', 'EMF', 'EMN', 'EMR', 'ENB', 'ENBL', 'ENIA', 'ENIC', 'ENJ', 'ENLC', 'ENO', 'ENPH', 'ENR', 'ENS', 'ENV', 'ENVA', 'ENZ', 'EOCC', 'EOG', 'EOI', 'EOS', 'EPAM', 'EPC', 'EPD', 'EPR', 'EPRT', 'EQC', 'EQH', 'EQR', 'ES', 'ESE', 'ESNT', 'ESRT', 'ESS', 'ESTC', 'ET', 'ETG', 'ETH', 'ETJ', 'ETN', 'ETO', 'ETR', 'ETRN', 'ETV', 'ETW', 'ETX', 'ETY', 'EURN', 'EV', 'EVA', 'EVC', 'EVF', 'EVG', 'EVH', 'EVN', 'EVR', 'EVRI', 'EVT', 'EVTC', 'EW', 'EXC', 'EXD', 'EXG', 'EXK', 'EXP', 'EXPR', 'EXR', 'EXTN', 'F', 'FAF', 'FAM', 'FBC', 'FBHS', 'FBP', 'FC', 'FCAU', 'FCF', 'FCN', 'FCPT', 'FCT', 'FCX', 'FDEU', 'FDP', 'FDS', 'FDX', 'FE', 'FEDU', 'FENG', 'FEO', 'FET', 'FF', 'FFA', 'FFC', 'FFG', 'FGB', 'FHI', 'FHN', 'FI', 'FICO', 'FIF', 'FINS', 'FIS', 'FIV', 'FIX', 'FL', 'FLC', 'FLNG', 'FLO', 'FLR', 'FLS', 'FLT', 'FLY', 'FMC', 'FMN', 'FMS', 'FMX', 'FMY', 'FN', 'FND', 'FNF', 'FOE', 'FOR', 'FOUR', 'FPF', 'FPH', 'FPI', 'FR', 'FRA', 'FRC', 'FRO', 'FRT', 'FSB', 'FSD', 'FSK', 'FSLY', 'FSM', 'FSS', 'FTCH', 'FTI', 'FTK', 'FTS', 'FTV', 'FUL', 'FUN', 'FVRR', 'G', 'GAB', 'GAM', 'GATX', 'GBL', 'GBX', 'GCI', 'GCO', 'GD', 'GDDY', 'GDO', 'GDOT', 'GDV', 'GE', 'GEF', 'GEL', 'GEN', 'GEO', 'GES', 'GF', 'GFF', 'GFI', 'GFL', 'GFY', 'GGB', 'GGG', 'GGM', 'GGT', 'GGZ', 'GHC', 'GHG', 'GHL', 'GHM', 'GHSI', 'GIB', 'GIL', 'GIS', 'GJH', 'GJO', 'GJP', 'GJR', 'GJS', 'GJT', 'GJV', 'GKOS', 'GL', 'GLW', 'GM', 'GME', 'GMED', 'GMS', 'GNK', 'GNL', 'GNRC', 'GNT', 'GNW', 'GOF', 'GOL', 'GPC', 'GPI', 'GPJA', 'GPK', 'GPM', 'GPMT', 'GPN', 'GPOR', 'GPRK', 'GPS', 'GRC', 'GRUB', 'GS', 'GSBD', 'GSK', 'GTN', 'GTS', 'GTY', 'GUT', 'GVA', 'GWB', 'GWRE', 'GWW', 'GYC', 'H', 'HAE', 'HAL', 'HASI', 'HAYW', 'HBM', 'HCA', 'HCC', 'HCI', 'HCXY', 'HD', 'HE', 'HEI', 'HEP', 'HES', 'HFC', 'HGV', 'HHC', 'HI', 'HIG', 'HII', 'HIO', 'HL', 'HLF', 'HLI', 'HLT', 'HMC', 'HMLP', 'HMN', 'HMY', 'HNGR', 'HNI', 'HOG', 'HOME', 'HON', 'HOV', 'HP', 'HPE', 'HPF', 'HPI', 'HPP', 'HPQ', 'HPS', 'HQH', 'HQL', 'HR', 'HRB', 'HRC', 'HRI', 'HRL', 'HRTG', 'HSBC', 'HSC', 'HSY', 'HT', 'HTA', 'HTD', 'HTFA', 'HTGC', 'HTH', 'HTY', 'HUBB', 'HUM', 'HUN', 'HUYA', 'HVT', 'HWM', 'HY', 'HYB', 'HYI', 'HYT', 'HZN', 'HZO', 'IAA', 'IAG', 'IBM', 'ICD', 'ICE', 'ICL', 'IDA', 'IDE', 'IDT', 'IEX', 'IFF', 'IGA', 'IGD', 'IGI', 'IGR', 'IGT', 'IHG', 'IHS', 'IIF', 'IIM', 'IMAX', 'ING', 'INGR', 'INSI', 'INSP', 'INT', 'IP', 'IPG', 'IPHI', 'IPI', 'IQV', 'IR', 'IRM', 'IRT', 'ISD', 'IT', 'ITGR', 'ITT', 'ITW', 'IVC', 'IVR', 'IVZ', 'J', 'JBL', 'JBLU', 'JBT', 'JCI', 'JEF', 'JELD', 'JHG', 'JHI', 'JHS', 'JHX', 'JILL', 'JKHY', 'JKS', 'JLL', 'JMM', 'JNJ', 'JNPR', 'JOE', 'JOF', 'JP', 'JPM', 'JPS', 'JPT', 'JQC', 'JRI', 'JRO', 'JRS', 'JSD', 'JT', 'JWN', 'K', 'KAI', 'KAMN', 'KB', 'KBH', 'KBR', 'KDMN', 'KDP', 'KEM', 'KEX', 'KEY', 'KEYS', 'KFS', 'KFY', 'KGC', 'KIM', 'KKR', 'KL', 'KMB', 'KMF', 'KMI', 'KMPR', 'KMT', 'KMX', 'KN', 'KNL', 'KNX', 'KO', 'KOF', 'KOP', 'KOS', 'KR', 'KRC', 'KREF', 'KRG', 'KRO', 'KRP', 'KSM', 'KSS', 'KSU', 'KT', 'KTB', 'KWR', 'L', 'LAD', 'LADR', 'LAIX', 'LAZ', 'LB', 'LBRT', 'LC', 'LCI', 'LCII', 'LDL', 'LDOS', 'LDP', 'LEA', 'LEE', 'LEG', 'LEN', 'LEVI', 'LFC', 'LGI', 'LH', 'LHX', 'LII', 'LIN', 'LIVN', 'LKQ', 'LLY', 'LMND', 'LMT', 'LNC', 'LND', 'LNN', 'LOAN', 'LOCK', 'LOW', 'LPG', 'LPI', 'LPL', 'LPX', 'LRN', 'LSI', 'LTC', 'LTHM', 'LUB', 'LUMN', 'LUV', 'LVS', 'LW', 'LXP', 'LXU', 'LYB', 'LYG', 'LYV', 'LZB', 'M', 'MA', 'MAA', 'MAC', 'MAN', 'MANU', 'MAS', 'MATX', 'MCD', 'MCI', 'MCK', 'MCN', 'MCO', 'MCR', 'MCS', 'MCY', 'MD', 'MDC', 'MDLA', 'MDLQ', 'MDLX', 'MDLY', 'MDP', 'MDT', 'MDU', 'MET', 'MFA', 'MFC', 'MFD', 'MFG', 'MFGP', 'MFL', 'MFM', 'MFO', 'MFT', 'MFV', 'MG', 'MGA', 'MGF', 'MGM', 'MGP', 'MGR', 'MGU', 'MGY', 'MHD', 'MHF', 'MHI', 'MHK', 'MHN', 'MHNC', 'MHO', 'MIC', 'MIN', 'MIT', 'MITT', 'MIXT', 'MIY', 'MKC', 'MKL', 'MLI', 'MLM', 'MLP', 'MLR', 'MMC', 'MMD', 'MMI', 'MMM', 'MMP', 'MMS', 'MMT', 'MMU', 'MN', 'MNP', 'MNR', 'MO', 'MOR', 'MOS', 'MOV', 'MPA', 'MPC', 'MPLX', 'MPV', 'MPW', 'MPX', 'MQT', 'MQY', 'MRK', 'MRO', 'MS', 'MSA', 'MSB', 'MSC', 'MSD', 'MSGE', 'MSGN', 'MSI', 'MSM', 'MT', 'MTB', 'MTD', 'MTDR', 'MTG', 'MTH', 'MTN', 'MTOR', 'MTR', 'MTRN', 'MTW', 'MTX', 'MTZ', 'MUA', 'MUC', 'MUE', 'MUFG', 'MUI', 'MUJ', 'MUR', 'MUSA', 'MUX', 'MVF', 'MVO', 'MVT', 'MWA', 'MX', 'MXE', 'MXF', 'MXI', 'MYC', 'MYD', 'MYE', 'MYF', 'MYI', 'MYJ', 'MYN', 'MYOV', 'MZA', 'NAC', 'NAD', 'NAN', 'NAT', 'NAV', 'NAZ', 'NBB', 'NBR', 'NC', 'NCA', 'NCR', 'NDP', 'NE', 'NEA', 'NEE', 'NEM', 'NEP', 'NET', 'NEU', 'NFG', 'NFH', 'NFJ', 'NGG', 'NGL', 'NGS', 'NGVC', 'NHA', 'NHF', 'NHI', 'NI', 'NID', 'NIE', 'NIM', 'NJR', 'NKE', 'NKG', 'NKX', 'NL', 'NLS', 'NLSN', 'NLY', 'NM', 'NMAI', 'NMCO', 'NMFC', 'NMI', 'NMM', 'NMR', 'NMS', 'NMT', 'NMZ', 'NNA', 'NNI', 'NNN', 'NOC', 'NOMD', 'NOV', 'NOVT', 'NOW', 'NP', 'NPK', 'NPO', 'NPTN', 'NPV', 'NQP', 'NR', 'NRE', 'NRG', 'NRK', 'NRP', 'NRT', 'NRUC', 'NRZ', 'NSA', 'NSC', 'NSP', 'NSS', 'NTB', 'NTCO', 'NTG', 'NTR', 'NTRS', 'NTZ', 'NUE', 'NUO', 'NUS', 'NUV', 'NUW', 'NVG', 'NVO', 'NVR', 'NVRO', 'NVS', 'NVST', 'NVT', 'NVTA', 'NWN', 'NWSA', 'NWS', 'NX', 'NXC', 'NXJ', 'NXN', 'NXP', 'NXQ', 'NXR', 'NYC', 'NYCB', 'NYT', 'NZF', 'O', 'OAK', 'OC', 'OCFT', 'OCN', 'ODC', 'OEC', 'OFC', 'OFG', 'OGS', 'OHI', 'OI', 'OIA', 'OII', 'OIS', 'OKE', 'OLN', 'OMC', 'OMF', 'ONB', 'ONE', 'OR', 'ORA', 'ORAN', 'ORC', 'ORCC', 'ORCL', 'ORI', 'ORN', 'OSK', 'OUT', 'OVV', 'OXM', 'OXY', 'PAC', 'PACW', 'PAG', 'PAI', 'PANW', 'PAR', 'PAYC', 'PB', 'PBA', 'PBF', 'PBI', 'PCF', 'PCG', 'PCI', 'PCK', 'PCM', 'PCN', 'PCQ', 'PDI', 'PDM', 'PDS', 'PDT', 'PEB', 'PEG', 'PEI', 'PEN', 'PEO', 'PER', 'PFE', 'PFGC', 'PFL', 'PFN', 'PFO', 'PFS', 'PFSI', 'PG', 'PGC', 'PGP', 'PGR', 'PGRE', 'PGTI', 'PGZ', 'PH', 'PHD', 'PHG', 'PHI', 'PHK', 'PHM', 'PHR', 'PHT', 'PHX', 'PIC', 'PII', 'PIM', 'PINE', 'PING', 'PINS', 'PIPR', 'PJC', 'PJT', 'PK', 'PKE', 'PKG', 'PKI', 'PKO', 'PKX', 'PLD', 'PLNT', 'PLOW', 'PLT', 'PM', 'PMF', 'PML', 'PMM', 'PMO', 'PMT', 'PMX', 'PNC', 'PNF', 'PNI', 'PNM', 'PNR', 'PNW', 'POL', 'POST', 'PPG', 'PPL', 'PPR', 'PPT', 'PRGO', 'PRH', 'PRI', 'PRLB', 'PRS', 'PRSP', 'PRT', 'PRU', 'PSA', 'PSB', 'PSF', 'PSN', 'PSO', 'PSTG', 'PSTL', 'PSX', 'PTR', 'PTY', 'PUK', 'PUMP', 'PVH', 'PVL', 'PWR', 'PXD', 'PYN', 'PYS', 'PYT', 'PZC', 'PZN', 'QD', 'QEP', 'QGEN', 'QRVO', 'R', 'RA', 'RACE', 'RAD', 'RBA', 'RBC', 'RBS', 'RC', 'RCA', 'RCB', 'RCI', 'RCL', 'RCS', 'RDN', 'RDY', 'RE', 'RELX', 'RENN', 'RES', 'REV', 'REVG', 'REX', 'REXR', 'REZI', 'RF', 'RFL', 'RFP', 'RGA', 'RGR', 'RGS', 'RH', 'RHI', 'RHP', 'RIG', 'RIO', 'RIV', 'RJF', 'RL', 'RLI', 'RLJ', 'RLX', 'RM', 'RMAX', 'RMD', 'RMI', 'RMM', 'RMP', 'RMT', 'RNG', 'RNP', 'RNR', 'RNST', 'ROC', 'ROG', 'ROK', 'ROL', 'ROP', 'ROYT', 'RPAI', 'RPL', 'RPM', 'RPT', 'RQI', 'RRC', 'RRD', 'RS', 'RSF', 'RSG', 'RTX', 'RVI', 'RVLV', 'RWT', 'RXN', 'RY', 'RYAM', 'RYB', 'RYI', 'RYN', 'RZA', 'RZB', 'SAF', 'SAFE', 'SAH', 'SAIC', 'SAIL', 'SALT', 'SAM', 'SAN', 'SAP', 'SAVE', 'SB', 'SBE', 'SBH', 'SBI', 'SBLK', 'SBNY', 'SBR', 'SBS', 'SBSW', 'SC', 'SCCO', 'SCD', 'SCE', 'SCHW', 'SCI', 'SCL', 'SCM', 'SCS', 'SCU', 'SCVX', 'SCWX', 'SCX', 'SD', 'SDRL', 'SE', 'SEAS', 'SEE', 'SEM', 'SES', 'SF', 'SFB', 'SFE', 'SFL', 'SFTW', 'SGEN', 'SGFY', 'SGU', 'SHAK', 'SHG', 'SHI', 'SHO', 'SHOP', 'SHW', 'SID', 'SIG', 'SII', 'SITC', 'SIX', 'SJI', 'SJM', 'SJR', 'SJT', 'SJW', 'SKM', 'SKT', 'SKX', 'SLB', 'SLCA', 'SLF', 'SLG', 'SLM', 'SM', 'SMAR', 'SMFG', 'SMG', 'SMLP', 'SMP', 'SNA', 'SNAP', 'SNN', 'SNP', 'SNR', 'SNV', 'SNX', 'SO', 'SOGO', 'SOI', 'SOL', 'SON', 'SONY', 'SPB', 'SPE', 'SPG', 'SPGI', 'SPH', 'SPL', 'SPR', 'SPT', 'SPXC', 'SPXX', 'SQ', 'SR', 'SRC', 'SRF', 'SRI', 'SRV', 'SSD', 'SSP', 'SSTK', 'ST', 'STAG', 'STAR', 'STC', 'STE', 'STG', 'STK', 'STL', 'STM', 'STN', 'STOR', 'STT', 'STWD', 'STX', 'STZ', 'SU', 'SUI', 'SUM', 'SUN', 'SUP', 'SUZ', 'SWCH', 'SWI', 'SWK', 'SWM', 'SWN', 'SWT', 'SWX', 'SWZ', 'SXC', 'SXI', 'SXT', 'SYF', 'SYK', 'SYX', 'SYY', 'T', 'TAC', 'TAK', 'TAL', 'TAP', 'TARO', 'TBB', 'TBC', 'TBI', 'TCI', 'TCO', 'TCP', 'TCRR', 'TCRW', 'TCRZ', 'TD', 'TDC', 'TDE', 'TDF', 'TDG', 'TDI', 'TDJ', 'TDOC', 'TDS', 'TDW', 'TDY', 'TEAF', 'TECK', 'TEF', 'TEL', 'TEN', 'TEO', 'TEVA', 'TFC', 'TFFP', 'TFX', 'TG', 'TGH', 'TGI', 'TGT', 'THC', 'THG', 'THO', 'THQ', 'THR', 'THS', 'TIF', 'TISI', 'TJX', 'TK', 'TKC', 'TKR', 'TLK', 'TLYS', 'TM', 'TME', 'TMHC', 'TMO', 'TMST', 'TNC', 'TNET', 'TNK', 'TNP', 'TOL', 'TORC', 'TOST', 'TPB', 'TPC', 'TPH', 'TPL', 'TPR', 'TPRE', 'TPVG', 'TPX', 'TR', 'TRAK', 'TRC', 'TREC', 'TREX', 'TRGP', 'TRI', 'TRN', 'TRNO', 'TROW', 'TRP', 'TRQ', 'TRTN', 'TRU', 'TRV', 'TS', 'TSCO', 'TSE', 'TSI', 'TSLA', 'TSLX', 'TSN', 'TSQ', 'TSU', 'TT', 'TTC', 'TTD', 'TTE', 'TTI', 'TTM', 'TTP', 'TU', 'TUP', 'TV', 'TVC', 'TVE', 'TW', 'TWI', 'TWLO', 'TWN', 'TWO', 'TWTR', 'TX', 'TXT', 'TY', 'TYG', 'TYL', 'UA', 'UAA', 'UAL', 'UAN', 'UBA', 'UBER', 'UBS', 'UDR', 'UE', 'UFS', 'UGI', 'UGP', 'UHS', 'UHT', 'UI', 'UIS', 'UL', 'UMC', 'UMH', 'UNF', 'UNFI', 'UNH', 'UNM', 'UNP', 'UNT', 'UNVR', 'UPS', 'URI', 'USA', 'USAC', 'USB', 'USDP', 'USFD', 'USM', 'USNA', 'USPH', 'USX', 'UTF', 'UTI', 'UTL', 'UTZ', 'UVE', 'UVV', 'UWMC', 'UZA', 'UZB', 'UZC', 'V', 'VAC', 'VAL', 'VALE', 'VAPO', 'VAR', 'VBF', 'VCIF', 'VCO', 'VCRA', 'VCV', 'VEC', 'VEDL', 'VEEV', 'VET', 'VFC', 'VGI', 'VGM', 'VGR', 'VHI', 'VICI', 'VIPS', 'VIST', 'VIV', 'VJET', 'VKQ', 'VLO', 'VLRS', 'VLT', 'VMC', 'VMI', 'VMO', 'VMW', 'VNCE', 'VNE', 'VNO', 'VNT', 'VOC', 'VOYA', 'VPG', 'VPV', 'VRA', 'VRE', 'VSH', 'VSLR', 'VST', 'VSTO', 'VTN', 'VTR', 'VTRS', 'VVI', 'VVR', 'VVV', 'VZ', 'W', 'WAB', 'WAL', 'WAT', 'WBA', 'WBS', 'WCC', 'WCN', 'WD', 'WDR', 'WEC', 'WELL', 'WES', 'WEX', 'WF', 'WFC', 'WGO', 'WH', 'WHR', 'WIA', 'WIT', 'WIW', 'WK', 'WLK', 'WLKP', 'WLL', 'WM', 'WMB', 'WMC', 'WMK', 'WMS', 'WMT', 'WNC', 'WOR', 'WOW', 'WPC', 'WPX', 'WRB', 'WRK', 'WSM', 'WSO', 'WST', 'WTBA', 'WTI', 'WTM', 'WTRG', 'WTS', 'WTTR', 'WU', 'WWE', 'WWW', 'WY', 'WYND', 'X', 'XEC', 'XEL', 'XFLT', 'XHR', 'XIN', 'XL', 'XLNX', 'XOM', 'XPO', 'XRAY', 'XRX', 'XYF', 'XYL', 'Y', 'YELP', 'YETI', 'YEXT', 'YUM', 'YUMC', 'ZBH', 'ZBRA', 'ZEN', 'ZIM', 'ZION', 'ZTO', 'ZTS', 'ZUO'
                    ]
                    
                    symbols = major_nyse[:limit]
                    self.stdout.write(f"[FALLBACK] Using {len(symbols)} major NYSE tickers")
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[ERROR] Failed to load NYSE tickers: {e}"))
                self.stdout.write(self.style.WARNING("[FALLBACK] Using database stocks only"))
                symbols = list(Stock.objects.filter(
                    exchange__iexact='NYSE'
                ).values_list('ticker', flat=True)[:limit])
        else:
            # Get all stocks from database
            symbols = list(Stock.objects.all().values_list('ticker', flat=True)[:limit])
        
        return symbols[:limit]

    def _filter_delisted_symbols(self, symbols, sample_size=100):
        """Pre-filter symbols to remove delisted/invalid ones"""
        if not symbols:
            return []
        
        self.stdout.write(f"[FILTER] Pre-filtering {len(symbols)} symbols to remove delisted ones...")
        self.stdout.write(f"[FILTER] Testing first {min(sample_size, len(symbols))} symbols...")
        self.stdout.flush()
        
        valid_symbols = []
        delisted_symbols = []
        
        # Test symbols in batches for efficiency
        test_symbols = symbols[:sample_size]
        
        for i, symbol in enumerate(test_symbols, 1):
            try:
                # Quick test with minimal delay
                time.sleep(0.02)  # Minimal delay for speed
                
                # Use a more robust approach
                ticker_obj = yf.Ticker(symbol)
                
                # Try to get basic info first
                try:
                    info = ticker_obj.info
                    has_info = info and isinstance(info, dict) and len(info) > 3
                except:
                    has_info = False
                
                # Try to get historical data with multiple approaches
                has_data = False
                hist = None
                
                # Method 1: Try different periods
                for period in ["1d", "5d", "1mo"]:
                    try:
                        hist = ticker_obj.history(period=period, timeout=5)
                        if hist is not None and not hist.empty and len(hist) > 0:
                            has_data = True
                            break
                    except Exception as e:
                        continue
                
                # Method 2: Try getting just the latest price
                if not has_data:
                    try:
                        latest = ticker_obj.history(period="1d", interval="1d", timeout=10)
                        if latest is not None and not latest.empty:
                            has_data = True
                            hist = latest
                    except:
                        pass
                
                # Method 3: Check if symbol exists at all
                if not has_data and not has_info:
                    try:
                        # Try a simple quote request
                        quote = ticker_obj.quote_type
                        if quote:
                            has_info = True
                    except:
                        pass
                
                # Determine if symbol is valid
                if has_data or has_info:
                    valid_symbols.append(symbol)
                    if i <= 10:  # Show first 10 valid
                        if has_data:
                            try:
                                price = hist['Close'].iloc[-1]
                                self.stdout.write(f"[VALID] {symbol}: ${price:.2f}")
                            except:
                                self.stdout.write(f"[VALID] {symbol}: Data available")
                        else:
                            self.stdout.write(f"[VALID] {symbol}: Info only")
                else:
                    delisted_symbols.append(symbol)
                    if i <= 20:  # Show first 20 delisted
                        self.stdout.write(f"[DELISTED] {symbol}: No data found")
                
                # Progress update every 20 symbols
                if i % 20 == 0:
                    self.stdout.write(f"[FILTER PROGRESS] {i}/{len(test_symbols)} - Valid: {len(valid_symbols)}, Delisted: {len(delisted_symbols)}")
                    self.stdout.flush()
                    
            except Exception as e:
                # If we get any error, assume it's delisted
                delisted_symbols.append(symbol)
                if i <= 20:  # Show first 20 errors
                    self.stdout.write(f"[DELISTED] {symbol}: Error - {str(e)[:50]}")
        
        # Calculate statistics
        if test_symbols:
            valid_percentage = len(valid_symbols) / len(test_symbols)
            delisted_percentage = len(delisted_symbols) / len(test_symbols)
            
            self.stdout.write(f"[FILTER STATS] Tested: {len(test_symbols)} symbols")
            self.stdout.write(f"[FILTER STATS] Valid: {len(valid_symbols)} ({valid_percentage*100:.1f}%)")
            self.stdout.write(f"[FILTER STATS] Delisted: {len(delisted_symbols)} ({delisted_percentage*100:.1f}%)")
            self.stdout.flush()
            
            # If we found very few valid symbols, the filtering might be too strict
            if valid_percentage < 0.1:  # Less than 10% valid
                self.stdout.write(f"[WARNING] Very low valid rate ({valid_percentage*100:.1f}%). Returning all symbols without filtering.")
                self.stdout.flush()
                return symbols
            
            # Estimate total valid symbols in full list
            estimated_valid = int(len(symbols) * valid_percentage)
            estimated_delisted = len(symbols) - estimated_valid
            
            self.stdout.write(f"[FILTER ESTIMATE] Full list: {len(symbols):,} symbols")
            self.stdout.write(f"[FILTER ESTIMATE] Expected valid: ~{estimated_valid:,} symbols")
            self.stdout.write(f"[FILTER ESTIMATE] Expected delisted: ~{estimated_delisted:,} symbols")
            self.stdout.flush()
            
            # Return only valid symbols from the test, plus remaining untested symbols
            remaining_symbols = symbols[sample_size:]
            final_symbols = valid_symbols + remaining_symbols
            
            self.stdout.write(f"[FILTER RESULT] Returning {len(final_symbols)} symbols for processing")
            self.stdout.write(f"[FILTER RESULT] Includes {len(valid_symbols)} pre-validated + {len(remaining_symbols)} untested")
            self.stdout.flush()
            
            return final_symbols
            
        return symbols

    def _process_stocks_batch(self, symbols, delay, test_mode, num_threads, batch_name="BATCH", no_proxy=False):
        """Process stocks with comprehensive data collection and proxy support"""
        start_time = time.time()
        total_symbols = len(symbols)
        successful = 0
        failed = 0
        
        # Initialize proxy manager only if not disabled
        proxy_manager = None
        if not no_proxy:
            try:
                proxy_manager = ProxyManager(min_proxies=50, max_proxies=200)
                stats = proxy_manager.get_proxy_stats()
                if stats['total_working'] > 0:
                    self.stdout.write(f"[PROXY] Proxy manager initialized with {stats['total_working']} working proxies")
                    self.stdout.write(f"[PROXY] Available: {stats['available']}, Used: {stats['used_in_run']}")
                else:
                    self.stdout.write(f"[PROXY] No proxies available initially - will try to refresh during run")
                    # Try to refresh the proxy pool
                    try:
                        count = proxy_manager.refresh_proxy_pool(force=True)
                        if count > 0:
                            stats = proxy_manager.get_proxy_stats()
                            self.stdout.write(f"[PROXY] Refreshed pool: {stats['total_working']} working proxies")
                        else:
                            self.stdout.write(f"[PROXY] Failed to refresh proxy pool - continuing without proxies")
                            proxy_manager = None
                    except Exception as refresh_error:
                        self.stdout.write(f"[PROXY] Refresh failed: {refresh_error} - continuing without proxies")
                        proxy_manager = None
            except Exception as e:
                self.stdout.write(f"[PROXY ERROR] Failed to initialize proxy manager: {e}")
                self.stdout.write(f"[PROXY] Continuing without proxies")
                proxy_manager = None
        else:
            self.stdout.write(f"[PROXY] Proxy usage disabled")
        
        # Add fallback: if no proxies available, disable proxy usage
        if proxy_manager:
            stats = proxy_manager.get_proxy_stats()
            if stats['total_working'] == 0:
                self.stdout.write(f"[PROXY FALLBACK] No working proxies available - disabling proxy usage")
                proxy_manager = None
        
        self.stdout.flush()
        
        # Add signal handler for graceful shutdown
        import signal
        stop_flag = threading.Event()
        lock = threading.Lock()
        processed = 0
        
        def signal_handler(signum, frame):
            stop_flag.set()
            self.stdout.write("\n[STOP] Signal received. Stopping gracefully...")
            self.stdout.flush()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        def update_counters(success):
            nonlocal successful, failed, processed
            with lock:
                if success:
                    successful += 1
                else:
                    failed += 1
                processed += 1
                # Update progress safely
                progress['current'] = processed
        
        def patch_yfinance_proxy(proxy):
            import yfinance
            if proxy:
                try:
                    session = requests.Session()
                    session.proxies = {
                        'http': proxy,
                        'https': proxy
                    }
                    # Set headers to avoid detection
                    session.headers.update({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    yfinance.shared._requests = session
                except Exception as e:
                    self.stdout.write(f"[PROXY ERROR] Failed to set proxy {proxy}: {e}")
                    yfinance.shared._requests = requests.Session()
            else:
                yfinance.shared._requests = requests.Session()
        
        def process_symbol(symbol, ticker_number):
            """Process a single symbol with comprehensive data collection"""
            try:
                # Get proxy for this ticker (switches every 200) - only if proxy manager exists
                proxy = None
                if proxy_manager:
                    proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
                    if proxy and ticker_number <= 5: # Show proxy info for first 5 tickers
                        self.stdout.write(f"[PROXY] {symbol}: Using proxy {proxy}")
                    elif not proxy and ticker_number % 100 == 0:  # Try to refresh every 100 tickers if no proxies
                        try:
                            count = proxy_manager.refresh_proxy_pool(force=True)
                            if count > 0:
                                self.stdout.write(f"[PROXY] Refreshed pool during run: {count} new proxies")
                                proxy = proxy_manager.get_proxy_for_ticker(ticker_number)
                        except Exception as e:
                            pass  # Silently continue without proxy
                
                # Set up yfinance with proxy (with better error handling)
                try:
                    patch_yfinance_proxy(proxy)
                except Exception as e:
                    # If proxy setup fails, continue without proxy
                    self.stdout.write(f"[PROXY ERROR] {symbol}: Failed to set proxy {proxy}: {e}")
                    patch_yfinance_proxy(None)
                
                # Minimal delay to avoid overwhelming the API
                time.sleep(random.uniform(0.01, 0.02))
                
                # Try multiple approaches to get data with shorter timeouts
                ticker_obj = yf.Ticker(symbol)
                info = None
                hist = None
                current_price = None
                
                # Approach 1: Try to get basic info (with timeout)
                try:
                    info = ticker_obj.info
                    if info and isinstance(info, dict) and len(info) > 3:
                        # Try to get current price from info first
                        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('regularMarketOpen')
                except Exception as e:
                    # Don't log every error to reduce noise
                    pass
                
                # Approach 2: Try to get historical data with shorter periods and timeouts
                if current_price is None:
                    for period in ["1d", "5d"]:  # Reduced periods for faster response
                        try:
                            hist = ticker_obj.history(period=period, timeout=5)  # Reduced timeout
                            if hist is not None and not hist.empty and len(hist) > 0:
                                try:
                                    current_price = hist['Close'].iloc[-1]
                                    if current_price is not None and not pd.isna(current_price):
                                        break
                                except:
                                    continue
                        except Exception as e:
                            # Check if it's a delisted symbol
                            err_str = str(e).lower()
                            if any(x in err_str for x in ['no data found', 'delisted', '404', 'symbol may be delisted']):
                                # Mark as delisted and skip further processing
                                update_counters(False)
                                return False
                            continue
                
                # Approach 3: Try a simple quote request as last resort
                if current_price is None:
                    try:
                        # Try to get basic quote info
                        quote = ticker_obj.quote_type
                        if quote:
                            # If we can get quote type, symbol exists but no price data
                            pass
                    except:
                        pass
                
                # Determine if we have enough data to process
                has_data = hist is not None and not hist.empty
                has_info = info and isinstance(info, dict) and len(info) > 3
                has_price = current_price is not None and not pd.isna(current_price)
                
                # If no data at all, mark as inactive and return
                if not has_data and not has_info and not has_price:
                    update_counters(False)
                    return False
                
                # Calculate price changes
                price_change_today = None
                change_percent = None
                if has_data and len(hist) > 1:
                    try:
                        prev_price = hist['Close'].iloc[-2]
                        if not pd.isna(prev_price) and prev_price > 0 and current_price:
                            price_change_today = current_price - prev_price
                            change_percent = (price_change_today / prev_price) * 100
                    except:
                        pass
                
                # Extract comprehensive data from info (with safe fallbacks)
                stock_data = {
                    'ticker': symbol,
                    'name': info.get('longName', info.get('shortName', symbol)) if info else symbol,
                    'sector': info.get('sector', 'Unknown') if info else 'Unknown',
                    'industry': info.get('industry', 'Unknown') if info else 'Unknown',
                    'market_cap': self._safe_decimal(info.get('marketCap')) if info else None,
                    'current_price': self._safe_decimal(current_price) if current_price else None,
                    'price_change': self._safe_decimal(price_change_today) if price_change_today else None,
                    'change_percent': self._safe_decimal(change_percent) if change_percent else None,
                    'volume': self._safe_decimal(info.get('volume', hist['Volume'].iloc[-1] if has_data and 'Volume' in hist.columns else None)) if (info or has_data) else None,
                    'avg_volume': self._safe_decimal(info.get('averageVolume')) if info else None,
                    'pe_ratio': self._safe_decimal(info.get('trailingPE')) if info else None,
                    'dividend_yield': self._safe_decimal(info.get('dividendYield')) if info else None,
                    'exchange': info.get('exchange', 'NYSE') if info else 'NYSE',
                    'currency': info.get('currency', 'USD') if info else 'USD',
                    'country': info.get('country', 'US') if info else 'US',
                    'is_active': True,
                    'last_updated': timezone.now()
                }
                
                # Save to database if not in test mode
                if not test_mode:
                    try:
                        stock, created = Stock.objects.update_or_create(
                            ticker=symbol,
                            defaults=stock_data
                        )
                        
                        # Save price data if we have historical data
                        if has_data and not hist.empty:
                            try:
                                latest_row = hist.iloc[-1]
                                price_data = {
                                    'stock': stock,
                                    'date': latest_row.name.date() if hasattr(latest_row.name, 'date') else timezone.now().date(),
                                    'open_price': self._safe_decimal(latest_row.get('Open')),
                                    'high_price': self._safe_decimal(latest_row.get('High')),
                                    'low_price': self._safe_decimal(latest_row.get('Low')),
                                    'close_price': self._safe_decimal(latest_row.get('Close')),
                                    'volume': self._safe_decimal(latest_row.get('Volume')),
                                    'created_at': timezone.now()
                                }
                                
                                StockPrice.objects.update_or_create(
                                    stock=stock,
                                    date=price_data['date'],
                                    defaults=price_data
                                )
                            except Exception as e:
                                # Log price save errors but don't fail the whole process
                                pass
                        
                        update_counters(True)
                        return True
                        
                    except Exception as e:
                        self.stdout.write(f"[DB ERROR] {symbol}: {e}")
                        update_counters(False)
                        return False
                else:
                    # Test mode - just return success
                    update_counters(True)
                    return True
                    
            except requests.exceptions.Timeout as e:
                self.stdout.write(f"[TIMEOUT] {symbol}: {e}")
                if proxy and proxy_manager:
                    proxy_manager.mark_proxy_failed(proxy)
                time.sleep(random.uniform(0.5, 1.0)) # Add delay for timeouts
                update_counters(False)
                return False
            except requests.exceptions.ConnectionError as e:
                self.stdout.write(f"[NETWORK] {symbol}: {e}")
                if proxy and proxy_manager:
                    proxy_manager.mark_proxy_failed(proxy)
                time.sleep(random.uniform(0.5, 1.0)) # Add delay for network errors
                update_counters(False)
                return False
            except Exception as e:
                # Log unexpected errors but don't let them stop the process
                err_str = str(e).lower()
                if any(x in err_str for x in ['no data found', 'delisted', '404', 'symbol may be delisted']):
                    # Don't log delisted symbols to reduce noise
                    update_counters(False)
                    return False
                else:
                    self.stdout.write(f"[ERROR] {symbol}: {e}")
                    update_counters(False)
                    return False
        
        # Process symbols individually
        self.stdout.write(f"[RUN] Starting {batch_name} with individual ticker processing...")
        self.stdout.flush()  # Force output

        progress = {'current': 0}
        
        def print_progress():
            while not stop_flag.is_set():
                try:
                    percent = (progress['current'] / total_symbols) * 100
                    elapsed = time.time() - start_time
                    self.stdout.write(f"[PROGRESS] {progress['current']}/{total_symbols} ({percent:.1f}%) - {elapsed:.1f}s elapsed")
                    self.stdout.flush()  # Force output
                    stop_flag.wait(10)
                except Exception as e:
                    self.stdout.write(f"[PROGRESS ERROR] {e}")
                    break
        
        progress_thread = threading.Thread(target=print_progress, daemon=True)
        progress_thread.start()

        # Add immediate feedback
        self.stdout.write(f"[START] Beginning to process {total_symbols} symbols...")
        self.stdout.flush()

        import concurrent.futures
        
        def process_symbol_with_timeout(symbol, ticker_number, timeout=15):
            """Process symbol with timeout using ThreadPoolExecutor"""
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(process_symbol, symbol, ticker_number)
                    return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                self.stdout.write(f"[TIMEOUT] {symbol} timed out after {timeout}s, skipping...")
                self.stdout.flush()
                update_counters(False)
                return False
            except Exception as e:
                self.stdout.write(f"[TIMEOUT ERROR] {symbol}: {e}")
                self.stdout.flush()
                update_counters(False)
                return False

        # Use ThreadPoolExecutor for true parallel processing
        self.stdout.write(f"[THREADS] Using {num_threads} threads for parallel processing")
        self.stdout.flush()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                # Submit all tasks
                future_to_symbol = {}
                for i, symbol in enumerate(symbols, 1):
                    if stop_flag.is_set():
                        break
                    future = executor.submit(process_symbol, symbol, i)
                    future_to_symbol[future] = (symbol, i)
                
                # Process completed tasks
                completed = 0
                for future in concurrent.futures.as_completed(future_to_symbol):
                    if stop_flag.is_set():
                        break
                        
                    symbol, i = future_to_symbol[future]
                    completed += 1
                    
                    try:
                        result = future.result(timeout=5)  # Reduced timeout to 5 seconds
                        if completed <= 10:  # Show first 10 results
                            self.stdout.write(f"[RESULT] {symbol}: {'SUCCESS' if result else 'FAILED'}")
                            self.stdout.flush()
                    except concurrent.futures.TimeoutError:
                        self.stdout.write(f"[TIMEOUT] {symbol} timed out after 5s")
                        self.stdout.flush()
                        update_counters(False)
                    except Exception as e:
                        self.stdout.write(f"[ERROR] {symbol}: {e}")
                        self.stdout.flush()
                        update_counters(False)
                    
                    # Update progress
                    progress['current'] = completed
                    
                    # Show progress every 100 completed tasks
                    if completed % 100 == 0 or completed == total_symbols:
                        progress_percent = (completed / total_symbols) * 100
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        self.stdout.write(f"[STATS] Progress: {completed}/{total_symbols} ({progress_percent:.1f}%) - {elapsed:.1f}s elapsed - {rate:.1f} symbols/sec")
                        self.stdout.flush()
                    
                    # Pause every 1000 symbols
                    if completed % 1000 == 0 and completed > 0:
                        if proxy_manager:
                            stats = proxy_manager.get_proxy_stats()
                            self.stdout.write(f"[PAUSE] Pausing for 10s after {completed} tickers...")
                            self.stdout.write(f"[PROXY STATS] Working: {stats['total_working']}, Used: {stats['used_in_run']}, Available: {stats['available']}")
                        else:
                            self.stdout.write(f"[PAUSE] Pausing for 10s after {completed} tickers... (no proxy)")
                        self.stdout.flush()
                        time.sleep(10)
        except KeyboardInterrupt:
            self.stdout.write("\n[STOP] Keyboard interrupt detected. Stopping gracefully...")
            self.stdout.write(f"[STOP] Processed {progress['current']} out of {total_symbols} symbols")
            self.stdout.flush()
            stop_flag.set()
            if progress_thread.is_alive():
                progress_thread.join(timeout=2)
            return {
                'total': progress['current'],
                'successful': successful,
                'failed': failed,
                'duration': time.time() - start_time,
                'interrupted': True
            }

        stop_flag.set()
        if progress_thread.is_alive():
            progress_thread.join(timeout=2)  # Wait max 2 seconds
        
        # Final proxy stats
        if proxy_manager:
            final_stats = proxy_manager.get_proxy_stats()
            self.stdout.write(f"[FINAL PROXY STATS] Total: {final_stats['total_working']}, Used: {final_stats['used_in_run']}")
        else:
            self.stdout.write(f"[FINAL PROXY STATS] No proxy used")
        self.stdout.flush()
        
        return {
            'total': total_symbols,
            'successful': successful,
            'failed': failed,
            'duration': time.time() - start_time
        }

    def _safe_decimal(self, value):
        """Safely convert value to Decimal, skip Infinity/NaN"""
        if value is None or pd.isna(value):
            return None
        try:
            d = Decimal(str(value))
            if d.is_infinite() or d.is_nan():
                return None
            return d
        except (ValueError, TypeError, Exception):
            return None

    def _test_yfinance_connectivity(self):
        """Test yfinance API connectivity with fallback"""
        try:
            # Try direct connectivity test first
            test_ticker = yf.Ticker("AAPL")
            test_info = test_ticker.info
            if test_info:
                self.stdout.write("[SUCCESS] yfinance connectivity test passed")
                return True
            else:
                self.stdout.write(self.style.WARNING("[WARNING] yfinance connectivity test failed - no data returned"))
                return False
        except Exception as e:
            error_str = str(e).lower()
            if 'could not resolve host' in error_str or 'dns' in error_str:
                self.stdout.write(self.style.WARNING("[WARNING] DNS resolution failed - this may be a network issue"))
                self.stdout.write(self.style.WARNING("[WARNING] Continuing anyway - yfinance may work with different endpoints"))
                return False
            elif 'timeout' in error_str:
                self.stdout.write(self.style.WARNING("[WARNING] yfinance connectivity timeout - continuing anyway"))
                return False
            else:
                self.stdout.write(self.style.WARNING(f"[WARNING] yfinance connectivity error: {e}"))
                self.stdout.write(self.style.WARNING("[WARNING] Continuing anyway - individual requests may still work"))
                return False

    def _display_final_results(self, results):
        """Display comprehensive final results"""
        duration = results['duration']
        success_rate = (results['successful'] / results['total']) * 100 if results['total'] > 0 else 0
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("[STATS] UPDATE COMPLETED"))
        self.stdout.write("="*70)
        self.stdout.write(f"[SUCCESS] Successful: {results['successful']}")
        self.stdout.write(f"[ERROR] Failed: {results['failed']}")
        self.stdout.write(f"[UP] Total processed: {results['total']}")
        self.stdout.write(f"[STATS] Success rate: {success_rate:.1f}%")
        self.stdout.write(f"[TIME]  Duration: {duration:.1f} seconds")
        self.stdout.write(f" Rate: {results['total']/duration:.1f} stocks/second")
        self.stdout.write(f" Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate < 80:
            self.stdout.write(self.style.WARNING(f"[WARNING]  Low success rate: {success_rate:.1f}%"))
        
        self.stdout.write("="*70)

    def _get_free_proxies(self):
        """Legacy method - now handled by ProxyManager"""
        return []