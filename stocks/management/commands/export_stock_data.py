import os
import json
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from stocks.models import StockAlert

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Export stock data to JSON format for filtering and email systems"

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-file', 
            type=str, 
            default=None,
            help='Custom output file path (default: json/stock_data_export.json)'
        )
        parser.add_argument(
            '--format', 
            choices=['web', 'email'], 
            default='web',
            help='Export format: web (for filtering) or email (for notifications)'
        )

    def handle(self, *args, **options):
        # Determine output file path
        if options['output_file']:
            output_file = options['output_file']
        else:
            # Default path expected by the web filtering system
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(BASE_DIR, '../../../../../json/stock_data_export.json')
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        format_type = options['format']
        
        try:
            # Get all stock data
            stocks = StockAlert.objects.all()
            
            if not stocks.exists():
                self.stdout.write(
                    self.style.WARNING('No stock data found. Run import_stock_data_optimized first.')
                )
                return
            
            if format_type == 'web':
                data = self._export_for_web(stocks)
            else:
                data = self._export_for_email(stocks)
            
            # Write to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Exported {len(data)} stock records to {output_file} (format: {format_type})'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Export failed: {e}')
            )
            raise

    def _export_for_web(self, stocks):
        """Export data format compatible with web filtering system"""
        data = []
        
        for stock in stocks:
            record = {
                'ticker': stock.ticker,
                'company_name': stock.company_name or '',
                'current_price': float(stock.current_price) if stock.current_price else 0.0,
                'volume_today': int(stock.volume_today) if stock.volume_today else 0,
                'avg_volume': int(stock.avg_volume) if stock.avg_volume else 0,
                'dvav': float(stock.dvav) if stock.dvav else 0.0,
                'dvsa': float(stock.dvsa) if stock.dvsa else 0.0,
                'pe_ratio': float(stock.pe_ratio) if stock.pe_ratio else 0.0,
                'market_cap': int(stock.market_cap) if stock.market_cap else 0,
                'note': stock.note or '',
                'last_update': stock.last_update.isoformat() if stock.last_update else '',
                'sent': stock.sent,
                
                # Additional computed fields for filtering
                'price_change_pct': self._calculate_price_change(stock),
                'volume_ratio': float(stock.dvav) if stock.dvav else 0.0,
                'shares_ratio': float(stock.dvsa) if stock.dvsa else 0.0,
            }
            data.append(record)
        
        return data

    def _export_for_email(self, stocks):
        """Export data format compatible with email notification system"""
        data = []
        
        # Only export stocks that haven't been sent via email
        unsent_stocks = stocks.filter(sent=False)
        
        for stock in unsent_stocks:
            record = {
                'stock_symbol': stock.ticker,
                'company_name': stock.company_name or '',
                'PRICE': str(stock.current_price) if stock.current_price else '0.00',
                'VOLUME': str(stock.volume_today) if stock.volume_today else '0',
                'DVAV': str(stock.dvav) if stock.dvav else '0.00',
                'DVSA': str(stock.dvsa) if stock.dvsa else '0.00',
                'PE': str(stock.pe_ratio) if stock.pe_ratio else '0.00',
                'MARKET_CAP': str(stock.market_cap) if stock.market_cap else '0',
                'note': stock.note or '',
                'category': self._categorize_stock(stock),
                'last_update': stock.last_update.isoformat() if stock.last_update else '',
            }
            data.append(record)
        
        return data

    def _calculate_price_change(self, stock):
        """Calculate price change percentage if possible"""
        # This would require historical data - placeholder for now
        return 0.0

    def _categorize_stock(self, stock):
        """Categorize stock based on note content for email filtering"""
        from emails.email_filter import EmailFilter
        
        filter = EmailFilter()
        category = filter.filter_email(stock.note.lower())
        return category if category != "Uncategorized" else ""