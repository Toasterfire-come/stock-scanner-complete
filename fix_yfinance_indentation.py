#!/usr/bin/env python3
"""
Fix indentation in update_stocks_yfinance.py
"""

import re
import sys

def fix_yfinance_indentation():
    """Fix indentation issues in the yfinance command file"""
    
    file_path = "stocks/management/commands/update_stocks_yfinance.py"
    
    print(f"Fixing indentation in {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        in_class = False
        in_method = False
        
        for i, line in enumerate(lines):
            # Track if we're in class or method
            if line.strip().startswith('class Command(BaseCommand):'):
                in_class = True
                fixed_lines.append(line)
                continue
            
            if in_class and line.strip().startswith('def '):
                in_method = True
                # Method should be indented 4 spaces from class
                fixed_lines.append('    ' + line.lstrip())
                continue
            
            if in_class and line.strip().startswith('help ='):
                # Class attributes should be indented 4 spaces
                fixed_lines.append('    ' + line.lstrip())
                continue
            
            if in_method and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                # Method content should be indented 8 spaces from start
                if line.strip().startswith(('parser.add_argument', 'self.', 'symbols =', 'limit =', 'batch_size =', 'delay =', 'test_mode =', 'log_level =', 'logging.', 'if ', 'for ', 'try:', 'except', 'return', 'results =', 'total_symbols =', 'processed =', 'successful =', 'failed =', 'skipped =', 'start_time =', 'batch_symbols =', 'batch_num =', 'total_batches =', 'batch_results =', 'progress =', 'elapsed =', 'eta =', 'time.sleep', 'quote_data =', 'updated =', 'stock_alert =', 'connection_tests =', 'usage_stats =')):
                    fixed_lines.append('        ' + line.lstrip())
                    continue
            
            # Handle multi-line argument definitions
            if in_method and (line.strip().startswith("'--") or line.strip().startswith('"--')):
                fixed_lines.append('            ' + line.lstrip())
                continue
            
            if in_method and line.strip() in ['type=str,', 'type=int,', 'type=float,', 'default=100,', 'default=10,', 'default=1.0,', "action='store_true',", 'help=']:
                fixed_lines.append('            ' + line.lstrip())
                continue
            
            # Keep original line if no specific rule applies
            fixed_lines.append(line)
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"[SUCCESS] Fixed indentation in {file_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error fixing {file_path}: {e}")
        return False

if __name__ == '__main__':
    fix_yfinance_indentation()