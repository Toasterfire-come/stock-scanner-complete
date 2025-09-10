<?php
/*
Template Name: Billing History
Description: Detailed billing history with invoices and exports
*/

get_header(); ?>

<div class="container mx-auto p-6">
    <div class="page-header mb-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Billing History</h1>
        <p class="text-gray-600">View and download your subscription invoices and payment history</p>
    </div>

    <!-- Billing Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="card p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                    </svg>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">Total Spent</h3>
                    <p class="text-2xl font-bold text-green-600" id="total-spent">$239.88</p>
                </div>
            </div>
        </div>

        <div class="card p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">Total Invoices</h3>
                    <p class="text-2xl font-bold text-blue-600" id="total-invoices">6</p>
                </div>
            </div>
        </div>

        <div class="card p-6">
            <div class="flex items-center">
                <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                    <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-900">Next Payment</h3>
                    <p class="text-2xl font-bold text-purple-600" id="next-payment">Feb 15</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters and Actions -->
    <div class="card p-6 mb-6">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div class="flex flex-col md:flex-row gap-4">
                <div>
                    <label for="year-filter" class="block text-sm font-medium text-gray-700 mb-1">Year</label>
                    <select id="year-filter" class="form-select rounded-lg border-gray-300">
                        <option value="">All Years</option>
                        <option value="2024" selected>2024</option>
                        <option value="2023">2023</option>
                    </select>
                </div>
                <div>
                    <label for="status-filter" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select id="status-filter" class="form-select rounded-lg border-gray-300">
                        <option value="">All Status</option>
                        <option value="paid">Paid</option>
                        <option value="pending">Pending</option>
                        <option value="failed">Failed</option>
                    </select>
                </div>
            </div>
            
            <div class="flex gap-2">
                <button onclick="exportBillingHistory('csv')" class="btn btn-secondary">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Export CSV
                </button>
                <button onclick="exportBillingHistory('pdf')" class="btn btn-primary">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    Export PDF
                </button>
            </div>
        </div>
    </div>

    <!-- Billing History Table -->
    <div class="card p-6">
        <div class="overflow-x-auto">
            <table class="w-full" id="billing-table">
                <thead>
                    <tr class="border-b border-gray-200">
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Invoice #</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Description</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Amount</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                        <th class="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
                    </tr>
                </thead>
                <tbody id="billing-tbody">
                    <!-- Sample data - will be replaced with dynamic content -->
                    <tr class="border-b border-gray-100 hover:bg-gray-50">
                        <td class="py-3 px-4 font-mono text-sm">#INV-2024-001</td>
                        <td class="py-3 px-4">Jan 15, 2024</td>
                        <td class="py-3 px-4">Silver Plan - Monthly Subscription</td>
                        <td class="py-3 px-4 font-semibold">$39.99</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Paid</span>
                        </td>
                        <td class="py-3 px-4">
                            <div class="flex gap-2">
                                <button onclick="viewInvoice('INV-2024-001')" class="text-blue-600 hover:text-blue-800 text-sm">View</button>
                                <button onclick="downloadInvoice('INV-2024-001')" class="text-green-600 hover:text-green-800 text-sm">Download</button>
                            </div>
                        </td>
                    </tr>
                    <tr class="border-b border-gray-100 hover:bg-gray-50">
                        <td class="py-3 px-4 font-mono text-sm">#INV-2023-012</td>
                        <td class="py-3 px-4">Dec 15, 2023</td>
                        <td class="py-3 px-4">Silver Plan - Monthly Subscription</td>
                        <td class="py-3 px-4 font-semibold">$39.99</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Paid</span>
                        </td>
                        <td class="py-3 px-4">
                            <div class="flex gap-2">
                                <button onclick="viewInvoice('INV-2023-012')" class="text-blue-600 hover:text-blue-800 text-sm">View</button>
                                <button onclick="downloadInvoice('INV-2023-012')" class="text-green-600 hover:text-green-800 text-sm">Download</button>
                            </div>
                        </td>
                    </tr>
                    <tr class="border-b border-gray-100 hover:bg-gray-50">
                        <td class="py-3 px-4 font-mono text-sm">#INV-2023-011</td>
                        <td class="py-3 px-4">Nov 15, 2023</td>
                        <td class="py-3 px-4">Bronze Plan - Monthly Subscription</td>
                        <td class="py-3 px-4 font-semibold">$24.99</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Paid</span>
                        </td>
                        <td class="py-3 px-4">
                            <div class="flex gap-2">
                                <button onclick="viewInvoice('INV-2023-011')" class="text-blue-600 hover:text-blue-800 text-sm">View</button>
                                <button onclick="downloadInvoice('INV-2023-011')" class="text-green-600 hover:text-green-800 text-sm">Download</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Invoice Modal -->
<div id="invoice-modal" class="modal-overlay" style="display: none;">
    <div class="modal-content max-w-4xl">
        <div class="modal-header">
            <h3 class="text-xl font-bold">Invoice Details</h3>
            <button onclick="closeInvoiceModal()" class="modal-close">&times;</button>
        </div>
        <div class="modal-body" id="invoice-content">
            <!-- Invoice content will be loaded here -->
        </div>
        <div class="modal-footer">
            <button onclick="downloadCurrentInvoice()" class="btn btn-primary">Download PDF</button>
            <button onclick="closeInvoiceModal()" class="btn btn-secondary">Close</button>
        </div>
    </div>
</div>

<style>
/* Billing History Specific Styles */
.billing-history {
    background: var(--color-bg);
    min-height: 100vh;
}

.card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: var(--shadow-md);
}

.btn {
    display: inline-flex;
    align-items: center;
    padding: var(--space-2) var(--space-4);
    font-weight: 500;
    border-radius: var(--radius-md);
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;
    text-decoration: none;
}

.btn-primary {
    background: var(--color-primary);
    color: var(--color-primary-contrast);
}

.btn-primary:hover {
    background: #1d4ed8;
    transform: translateY(-1px);
}

.btn-secondary {
    background: var(--color-surface);
    color: var(--color-text);
    border: 1px solid var(--color-border);
}

.btn-secondary:hover {
    background: var(--color-border);
}

.form-select {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    color: var(--color-text);
    padding: var(--space-2) var(--space-3);
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: var(--shadow-lg);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-6);
    border-bottom: 1px solid var(--color-border);
}

.modal-body {
    padding: var(--space-6);
}

.modal-footer {
    padding: var(--space-6);
    border-top: 1px solid var(--color-border);
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3);
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--color-text-muted);
}

.modal-close:hover {
    color: var(--color-text);
}

table {
    border-collapse: collapse;
}

table th,
table td {
    text-align: left;
}

@media (max-width: 768px) {
    .card {
        margin: var(--space-2);
    }
    
    .table-responsive {
        overflow-x: auto;
    }
    
    .modal-content {
        margin: var(--space-4);
        max-width: calc(100vw - 32px);
    }
}
</style>

<script>
// Billing History JavaScript
class BillingHistoryManager {
    constructor() {
        this.currentInvoice = null;
        this.initializeFilters();
    }
    
    initializeFilters() {
        document.getElementById('year-filter').addEventListener('change', (e) => this.filterBilling());
        document.getElementById('status-filter').addEventListener('change', (e) => this.filterBilling());
    }
    
    filterBilling() {
        const yearFilter = document.getElementById('year-filter').value;
        const statusFilter = document.getElementById('status-filter').value;
        
        // In real implementation, this would make an API call
        console.log('Filtering by year:', yearFilter, 'status:', statusFilter);
        
        // Mock filtering for demo
        const rows = document.querySelectorAll('#billing-tbody tr');
        rows.forEach(row => {
            let showRow = true;
            
            if (yearFilter && !row.cells[1].textContent.includes(yearFilter)) {
                showRow = false;
            }
            
            if (statusFilter) {
                const statusElement = row.querySelector('.rounded-full');
                const status = statusElement.textContent.toLowerCase();
                if (status !== statusFilter) {
                    showRow = false;
                }
            }
            
            row.style.display = showRow ? '' : 'none';
        });
    }
}

// Initialize billing history manager
const billingManager = new BillingHistoryManager();

// Export functions
function exportBillingHistory(format) {
    const data = getBillingData();
    
    if (format === 'csv') {
        exportToCSV(data);
    } else if (format === 'pdf') {
        exportToPDF(data);
    }
}

function getBillingData() {
    // In real implementation, get data from API
    return [
        {
            invoice: 'INV-2024-001',
            date: '2024-01-15',
            description: 'Silver Plan - Monthly Subscription',
            amount: '$39.99',
            status: 'Paid'
        },
        {
            invoice: 'INV-2023-012',
            date: '2023-12-15',
            description: 'Silver Plan - Monthly Subscription',
            amount: '$39.99',
            status: 'Paid'
        },
        {
            invoice: 'INV-2023-011',
            date: '2023-11-15',
            description: 'Bronze Plan - Monthly Subscription',
            amount: '$24.99',
            status: 'Paid'
        }
    ];
}

function exportToCSV(data) {
    const headers = ['Invoice', 'Date', 'Description', 'Amount', 'Status'];
    const csvContent = [
        headers.join(','),
        ...data.map(row => [
            row.invoice,
            row.date,
            `"${row.description}"`,
            row.amount,
            row.status
        ].join(','))
    ].join('\n');
    
    downloadFile(csvContent, 'billing-history.csv', 'text/csv');
}

function exportToPDF(data) {
    // Mock PDF export - in real implementation, generate actual PDF
    const pdfContent = `
        Billing History Report
        Generated: ${new Date().toLocaleDateString()}
        
        ${data.map(row => 
            `${row.invoice} | ${row.date} | ${row.description} | ${row.amount} | ${row.status}`
        ).join('\n')}
    `;
    
    downloadFile(pdfContent, 'billing-history.pdf', 'application/pdf');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Invoice modal functions
function viewInvoice(invoiceId) {
    const modal = document.getElementById('invoice-modal');
    const content = document.getElementById('invoice-content');
    
    // Mock invoice content - in real implementation, fetch from API
    content.innerHTML = generateInvoiceHTML(invoiceId);
    modal.style.display = 'flex';
    billingManager.currentInvoice = invoiceId;
}

function generateInvoiceHTML(invoiceId) {
    return `
        <div class="invoice-document">
            <div class="invoice-header mb-6">
                <div class="flex justify-between items-start">
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900">INVOICE</h2>
                        <p class="text-gray-600">${invoiceId}</p>
                    </div>
                    <div class="text-right">
                        <p class="font-semibold">Stock Scanner Pro</p>
                        <p class="text-sm text-gray-600">support@stockscanner.com</p>
                    </div>
                </div>
            </div>
            
            <div class="invoice-details grid grid-cols-2 gap-6 mb-6">
                <div>
                    <h3 class="font-semibold mb-2">Bill To:</h3>
                    <p>John Doe</p>
                    <p>john.doe@example.com</p>
                    <p>User ID: 12345</p>
                </div>
                <div>
                    <h3 class="font-semibold mb-2">Invoice Details:</h3>
                    <p>Date: January 15, 2024</p>
                    <p>Due Date: January 15, 2024</p>
                    <p>Status: Paid</p>
                </div>
            </div>
            
            <div class="invoice-items">
                <table class="w-full mb-6">
                    <thead>
                        <tr class="border-b">
                            <th class="text-left py-2">Description</th>
                            <th class="text-right py-2">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="py-2">Silver Plan - Monthly Subscription</td>
                            <td class="text-right py-2">$39.99</td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr class="border-t font-semibold">
                            <td class="py-2">Total</td>
                            <td class="text-right py-2">$39.99</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
            
            <div class="invoice-footer text-sm text-gray-600">
                <p>Thank you for your business!</p>
                <p>If you have any questions, please contact support@stockscanner.com</p>
            </div>
        </div>
    `;
}

function downloadInvoice(invoiceId) {
    // Mock download - in real implementation, generate PDF
    console.log('Downloading invoice:', invoiceId);
    
    // Create a simple text version for demo
    const invoiceContent = `
        INVOICE ${invoiceId}
        
        Date: January 15, 2024
        Amount: $39.99
        Description: Silver Plan - Monthly Subscription
        Status: Paid
        
        Thank you for your business!
    `;
    
    downloadFile(invoiceContent, `invoice-${invoiceId}.txt`, 'text/plain');
}

function downloadCurrentInvoice() {
    if (billingManager.currentInvoice) {
        downloadInvoice(billingManager.currentInvoice);
    }
}

function closeInvoiceModal() {
    document.getElementById('invoice-modal').style.display = 'none';
    billingManager.currentInvoice = null;
}

// Close modal when clicking outside
document.getElementById('invoice-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeInvoiceModal();
    }
});
</script>

<?php get_footer(); ?>