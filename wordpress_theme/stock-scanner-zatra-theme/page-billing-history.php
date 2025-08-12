<?php
/**
 * Template Name: Billing History
 * 
 * The template for displaying user billing history and payment records
 */

// Redirect to login if not authenticated
if (!is_user_logged_in()) {
    wp_redirect(wp_login_url(get_permalink()));
    exit;
}

get_header(); 
?>

<div class="billing-history-container">
    <div class="page-header">
        <div class="container">
            <h1 class="page-title">
                <i class="fas fa-receipt"></i>
                Billing History
            </h1>
            <p class="page-subtitle">View your payment history, invoices, and manage your subscription</p>
        </div>
    </div>

    <div class="billing-content">
        <div class="container">
            <div class="billing-layout">
                <!-- Billing Summary -->
                <div class="billing-summary">
                    <div class="summary-card current-plan">
                        <div class="card-header">
                            <h3>Current Plan</h3>
                            <span class="plan-status active">Active</span>
                        </div>
                        <div class="card-content">
                            <div class="plan-info">
                                <div class="plan-name">Pro Plan</div>
                                <div class="plan-price">$29.99/month</div>
                                <div class="plan-features">
                                    Real-time data • Unlimited watchlists • Premium alerts
                                </div>
                            </div>
                            <div class="plan-actions">
                                <a href="/premium-plans/" class="btn btn-outline">Change Plan</a>
                                <button class="btn btn-danger" onclick="cancelSubscription()">Cancel</button>
                            </div>
                        </div>
                    </div>

                    <div class="summary-cards-grid">
                        <div class="summary-card">
                            <div class="card-icon">
                                <i class="fas fa-calendar-alt"></i>
                            </div>
                            <div class="card-info">
                                <div class="card-value">Feb 15, 2024</div>
                                <div class="card-label">Next Billing Date</div>
                            </div>
                        </div>

                        <div class="summary-card">
                            <div class="card-icon">
                                <i class="fas fa-credit-card"></i>
                            </div>
                            <div class="card-info">
                                <div class="card-value">•••• 4321</div>
                                <div class="card-label">Payment Method</div>
                            </div>
                        </div>

                        <div class="summary-card">
                            <div class="card-icon">
                                <i class="fas fa-dollar-sign"></i>
                            </div>
                            <div class="card-info">
                                <div class="card-value">$359.88</div>
                                <div class="card-label">Total Spent</div>
                            </div>
                        </div>

                        <div class="summary-card">
                            <div class="card-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="card-info">
                                <div class="card-value">12 months</div>
                                <div class="card-label">Member Since</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Billing History Table -->
                <div class="billing-history">
                    <div class="section-header">
                        <h2>Payment History</h2>
                        <div class="history-controls">
                            <div class="filter-controls">
                                <select id="yearFilter" class="form-select">
                                    <option value="">All Years</option>
                                    <option value="2024" selected>2024</option>
                                    <option value="2023">2023</option>
                                </select>
                                <select id="statusFilter" class="form-select">
                                    <option value="">All Status</option>
                                    <option value="paid">Paid</option>
                                    <option value="pending">Pending</option>
                                    <option value="failed">Failed</option>
                                </select>
                            </div>
                            <button class="btn btn-outline" id="exportHistory">
                                <i class="fas fa-download"></i>
                                Export
                            </button>
                        </div>
                    </div>

                    <div class="billing-table-container">
                        <div class="billing-table">
                            <div class="table-header">
                                <div class="header-cell">Invoice</div>
                                <div class="header-cell">Date</div>
                                <div class="header-cell">Description</div>
                                <div class="header-cell">Amount</div>
                                <div class="header-cell">Status</div>
                                <div class="header-cell">Actions</div>
                            </div>
                            
                            <div class="table-body" id="billingTableBody">
                                <!-- Billing records will be loaded here -->
                            </div>
                        </div>

                        <div class="loading-state" id="billingLoading">
                            <div class="loading-spinner"></div>
                            <p>Loading billing history...</p>
                        </div>

                        <div class="empty-state" id="billingEmpty" style="display: none;">
                            <div class="empty-icon">
                                <i class="fas fa-receipt"></i>
                            </div>
                            <h3>No billing history found</h3>
                            <p>Your payment history will appear here once you make your first payment.</p>
                            <a href="/premium-plans/" class="btn btn-primary">View Plans</a>
                        </div>
                    </div>

                    <div class="pagination" id="billingPagination" style="display: none;">
                        <button class="btn btn-outline" id="prevPage" disabled>
                            <i class="fas fa-chevron-left"></i>
                            Previous
                        </button>
                        <span class="page-info" id="pageInfo">Page 1 of 1</span>
                        <button class="btn btn-outline" id="nextPage" disabled>
                            Next
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                </div>

                <!-- Payment Method Management -->
                <div class="payment-methods">
                    <div class="section-header">
                        <h2>Payment Methods</h2>
                        <button class="btn btn-primary" id="addPaymentMethod">
                            <i class="fas fa-plus"></i>
                            Add Payment Method
                        </button>
                    </div>

                    <div class="payment-methods-list" id="paymentMethodsList">
                        <!-- Payment methods will be loaded here -->
                    </div>
                </div>

                <!-- Subscription Management -->
                <div class="subscription-management">
                    <div class="section-header">
                        <h2>Subscription Management</h2>
                    </div>

                    <div class="subscription-details">
                        <div class="detail-section">
                            <h3>Billing Information</h3>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <label>Billing Cycle</label>
                                    <span>Monthly</span>
                                </div>
                                <div class="detail-item">
                                    <label>Auto-Renewal</label>
                                    <span class="status-active">Enabled</span>
                                </div>
                                <div class="detail-item">
                                    <label>Tax Rate</label>
                                    <span>8.25%</span>
                                </div>
                                <div class="detail-item">
                                    <label>Currency</label>
                                    <span>USD</span>
                                </div>
                            </div>
                        </div>

                        <div class="detail-section">
                            <h3>Usage & Limits</h3>
                            <div class="usage-bars">
                                <div class="usage-item">
                                    <div class="usage-header">
                                        <span>API Calls</span>
                                        <span>8,450 / 10,000</span>
                                    </div>
                                    <div class="usage-bar">
                                        <div class="usage-fill" style="width: 84.5%"></div>
                                    </div>
                                </div>
                                <div class="usage-item">
                                    <div class="usage-header">
                                        <span>Watchlists</span>
                                        <span>7 / Unlimited</span>
                                    </div>
                                    <div class="usage-bar">
                                        <div class="usage-fill unlimited" style="width: 100%"></div>
                                    </div>
                                </div>
                                <div class="usage-item">
                                    <div class="usage-header">
                                        <span>Alerts</span>
                                        <span>23 / 50</span>
                                    </div>
                                    <div class="usage-bar">
                                        <div class="usage-fill" style="width: 46%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Invoice Modal -->
<div class="modal" id="invoiceModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Invoice Details</h3>
            <button class="modal-close" onclick="closeInvoiceModal()">&times;</button>
        </div>
        <div class="modal-body" id="invoiceModalBody">
            <!-- Invoice details will be loaded here -->
        </div>
        <div class="modal-footer">
            <button class="btn btn-outline" onclick="closeInvoiceModal()">Close</button>
            <button class="btn btn-primary" id="downloadInvoice">
                <i class="fas fa-download"></i>
                Download PDF
            </button>
        </div>
    </div>
</div>

<style>
.billing-history-container {
    min-height: 100vh;
    background: #f8f9fa;
}

.page-header {
    background: linear-gradient(135deg, #3685fb 0%, #2563eb 100%);
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.page-title {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.page-subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
    margin: 1rem 0 0 0;
}

.billing-content {
    padding: 3rem 0;
}

.billing-layout {
    display: flex;
    flex-direction: column;
    gap: 3rem;
}

.billing-summary {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
    align-items: start;
}

.summary-card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.current-plan .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.current-plan h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.plan-status {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.plan-status.active {
    background: #dcfce7;
    color: #166534;
}

.plan-info {
    margin-bottom: 2rem;
}

.plan-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}

.plan-price {
    font-size: 2rem;
    font-weight: 700;
    color: #3685fb;
    margin-bottom: 0.5rem;
}

.plan-features {
    color: #666;
    font-size: 0.95rem;
}

.plan-actions {
    display: flex;
    gap: 1rem;
}

.summary-cards-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}

.summary-cards-grid .summary-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
}

.card-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #f0f9ff;
    color: #3685fb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
}

.card-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.25rem;
}

.card-label {
    color: #666;
    font-size: 0.9rem;
}

.billing-history,
.payment-methods,
.subscription-management {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e1e5e9;
}

.section-header h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0;
}

.history-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.filter-controls {
    display: flex;
    gap: 0.5rem;
}

.form-select {
    padding: 0.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 6px;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
}

.form-select:focus {
    border-color: #3685fb;
    box-shadow: 0 0 0 3px rgba(54, 133, 251, 0.1);
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
}

.btn-primary {
    background: #3685fb;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-outline {
    background: transparent;
    color: #666;
    border: 1px solid #e1e5e9;
}

.btn-outline:hover {
    background: #f8f9fa;
    border-color: #3685fb;
    color: #3685fb;
}

.btn-danger {
    background: #ef4444;
    color: white;
}

.btn-danger:hover {
    background: #dc2626;
}

.billing-table-container {
    position: relative;
    min-height: 400px;
}

.billing-table {
    width: 100%;
}

.table-header {
    background: #f8f9fa;
    display: grid;
    grid-template-columns: 120px 120px 1fr 120px 100px 120px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #e1e5e9;
    font-weight: 600;
    color: #333;
    font-size: 0.9rem;
}

.table-body {
    max-height: 600px;
    overflow-y: auto;
}

.billing-row {
    display: grid;
    grid-template-columns: 120px 120px 1fr 120px 100px 120px;
    gap: 1rem;
    padding: 1rem;
    border-bottom: 1px solid #f0f0f0;
    align-items: center;
    transition: background 0.2s;
    font-size: 0.9rem;
}

.billing-row:hover {
    background: #f8f9fa;
}

.invoice-number {
    font-weight: 600;
    color: #3685fb;
    cursor: pointer;
}

.invoice-number:hover {
    text-decoration: underline;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    text-align: center;
}

.status-paid {
    background: #dcfce7;
    color: #166534;
}

.status-pending {
    background: #fef3c7;
    color: #92400e;
}

.status-failed {
    background: #fee2e2;
    color: #991b1b;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.action-btn {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.2s;
    font-size: 0.9rem;
}

.action-btn:hover {
    background: #f0f0f0;
    color: #3685fb;
}

.loading-state,
.empty-state {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: white;
    text-align: center;
    padding: 3rem;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e1e5e9;
    border-top: 3px solid #3685fb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.empty-icon {
    font-size: 4rem;
    color: #ddd;
    margin-bottom: 1rem;
}

.empty-state h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.empty-state p {
    margin: 0 0 2rem 0;
    color: #666;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e1e5e9;
}

.page-info {
    font-size: 0.9rem;
    color: #666;
}

.payment-methods-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.payment-method {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    transition: border-color 0.2s;
}

.payment-method:hover {
    border-color: #3685fb;
}

.payment-method.default {
    border-color: #3685fb;
    background: #f0f9ff;
}

.method-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.method-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    color: #666;
}

.method-details h4 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a1a;
}

.method-details p {
    margin: 0;
    font-size: 0.9rem;
    color: #666;
}

.method-actions {
    display: flex;
    gap: 0.5rem;
}

.subscription-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
}

.detail-section h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 1.5rem 0;
}

.detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.detail-item label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #666;
}

.detail-item span {
    font-size: 1rem;
    font-weight: 600;
    color: #1a1a1a;
}

.status-active {
    color: #10b981;
}

.usage-bars {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.usage-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.usage-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
}

.usage-header span:first-child {
    font-weight: 500;
    color: #666;
}

.usage-header span:last-child {
    font-weight: 600;
    color: #1a1a1a;
}

.usage-bar {
    height: 8px;
    background: #e1e5e9;
    border-radius: 4px;
    overflow: hidden;
}

.usage-fill {
    height: 100%;
    background: #3685fb;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.usage-fill.unlimited {
    background: linear-gradient(90deg, #10b981, #059669);
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    align-items: center;
    justify-content: center;
}

.modal.show {
    display: flex;
}

.modal-content {
    background: white;
    border-radius: 12px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 2rem 1rem;
    border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a1a;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #666;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-body {
    padding: 2rem;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding: 1rem 2rem 2rem;
    border-top: 1px solid #e1e5e9;
}

@media (max-width: 1024px) {
    .billing-summary {
        grid-template-columns: 1fr;
    }
    
    .summary-cards-grid {
        grid-template-columns: 1fr;
    }
    
    .subscription-details {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}

@media (max-width: 768px) {
    .page-title {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .section-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .history-controls {
        justify-content: space-between;
    }
    
    .table-header,
    .billing-row {
        grid-template-columns: 1fr 100px 80px 100px;
        font-size: 0.8rem;
    }
    
    .table-header .header-cell:nth-child(2),
    .billing-row > *:nth-child(2),
    .table-header .header-cell:nth-child(3),
    .billing-row > *:nth-child(3) {
        display: none;
    }
    
    .plan-actions {
        flex-direction: column;
    }
    
    .detail-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    initializeBillingHistory();
    loadBillingData();
    loadPaymentMethods();
});

let currentPage = 1;
let totalPages = 1;
let currentFilters = {};

function initializeBillingHistory() {
    // Filter controls
    document.getElementById('yearFilter').addEventListener('change', applyFilters);
    document.getElementById('statusFilter').addEventListener('change', applyFilters);
    
    // Export button
    document.getElementById('exportHistory').addEventListener('click', exportBillingHistory);
    
    // Pagination
    document.getElementById('prevPage').addEventListener('click', () => changePage(currentPage - 1));
    document.getElementById('nextPage').addEventListener('click', () => changePage(currentPage + 1));
    
    // Add payment method
    document.getElementById('addPaymentMethod').addEventListener('click', addPaymentMethod);
}

function loadBillingData() {
    showLoading();
    
    // Simulate API call to load billing history
    setTimeout(() => {
        const billingData = generateMockBillingData();
        displayBillingData(billingData);
        hideLoading();
    }, 1500);
}

function generateMockBillingData() {
    const invoices = [
        { id: 'INV-2024-001', date: '2024-01-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-012', date: '2023-12-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-011', date: '2023-11-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-010', date: '2023-10-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'failed' },
        { id: 'INV-2023-009', date: '2023-09-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-008', date: '2023-08-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-007', date: '2023-07-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-006', date: '2023-06-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-005', date: '2023-05-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-004', date: '2023-04-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-003', date: '2023-03-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' },
        { id: 'INV-2023-002', date: '2023-02-15', description: 'Pro Plan - Monthly', amount: 29.99, status: 'paid' }
    ];
    
    return invoices;
}

function displayBillingData(data) {
    const tableBody = document.getElementById('billingTableBody');
    
    if (data.length === 0) {
        document.getElementById('billingEmpty').style.display = 'flex';
        return;
    }
    
    tableBody.innerHTML = data.map(invoice => {
        const statusClass = `status-${invoice.status}`;
        const formattedDate = new Date(invoice.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        return `
            <div class="billing-row">
                <div class="invoice-number" onclick="viewInvoice('${invoice.id}')">${invoice.id}</div>
                <div>${formattedDate}</div>
                <div>${invoice.description}</div>
                <div>$${invoice.amount.toFixed(2)}</div>
                <div>
                    <span class="status-badge ${statusClass}">${invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}</span>
                </div>
                <div class="action-buttons">
                    <button class="action-btn" onclick="viewInvoice('${invoice.id}')" title="View Invoice">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" onclick="downloadInvoice('${invoice.id}')" title="Download PDF">
                        <i class="fas fa-download"></i>
                    </button>
                    ${invoice.status === 'failed' ? `<button class="action-btn" onclick="retryPayment('${invoice.id}')" title="Retry Payment"><i class="fas fa-redo"></i></button>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function loadPaymentMethods() {
    const paymentMethodsList = document.getElementById('paymentMethodsList');
    
    const paymentMethods = [
        {
            id: 'pm_1',
            type: 'card',
            brand: 'visa',
            last4: '4321',
            expiry: '12/25',
            isDefault: true
        },
        {
            id: 'pm_2',
            type: 'paypal',
            email: 'user@example.com',
            isDefault: false
        }
    ];
    
    paymentMethodsList.innerHTML = paymentMethods.map(method => {
        const isCard = method.type === 'card';
        const icon = isCard ? 'fas fa-credit-card' : 'fab fa-paypal';
        const title = isCard ? `${method.brand.toUpperCase()} •••• ${method.last4}` : 'PayPal';
        const subtitle = isCard ? `Expires ${method.expiry}` : method.email;
        
        return `
            <div class="payment-method ${method.isDefault ? 'default' : ''}">
                <div class="method-info">
                    <div class="method-icon">
                        <i class="${icon}"></i>
                    </div>
                    <div class="method-details">
                        <h4>${title}</h4>
                        <p>${subtitle}</p>
                        ${method.isDefault ? '<p><strong>Default payment method</strong></p>' : ''}
                    </div>
                </div>
                <div class="method-actions">
                    ${!method.isDefault ? `<button class="action-btn" onclick="setDefaultPayment('${method.id}')" title="Set as Default"><i class="fas fa-star"></i></button>` : ''}
                    <button class="action-btn" onclick="editPaymentMethod('${method.id}')" title="Edit"><i class="fas fa-edit"></i></button>
                    <button class="action-btn" onclick="deletePaymentMethod('${method.id}')" title="Delete"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    }).join('');
}

function showLoading() {
    document.getElementById('billingLoading').style.display = 'flex';
    document.getElementById('billingEmpty').style.display = 'none';
}

function hideLoading() {
    document.getElementById('billingLoading').style.display = 'none';
}

function applyFilters() {
    const year = document.getElementById('yearFilter').value;
    const status = document.getElementById('statusFilter').value;
    
    currentFilters = { year, status };
    currentPage = 1;
    
    showLoading();
    
    // Simulate filtered data loading
    setTimeout(() => {
        let data = generateMockBillingData();
        
        if (year) {
            data = data.filter(invoice => invoice.date.startsWith(year));
        }
        
        if (status) {
            data = data.filter(invoice => invoice.status === status);
        }
        
        displayBillingData(data);
        hideLoading();
    }, 800);
}

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    loadBillingData();
}

function viewInvoice(invoiceId) {
    const modal = document.getElementById('invoiceModal');
    const modalBody = document.getElementById('invoiceModalBody');
    
    // Simulate loading invoice details
    modalBody.innerHTML = `
        <div class="invoice-details">
            <div class="invoice-header">
                <h4>Invoice ${invoiceId}</h4>
                <div class="invoice-date">Date: January 15, 2024</div>
            </div>
            <div class="invoice-items">
                <div class="invoice-item">
                    <span>Pro Plan - Monthly Subscription</span>
                    <span>$29.99</span>
                </div>
                <div class="invoice-item">
                    <span>Tax (8.25%)</span>
                    <span>$2.47</span>
                </div>
                <div class="invoice-total">
                    <span><strong>Total</strong></span>
                    <span><strong>$32.46</strong></span>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.add('show');
}

function closeInvoiceModal() {
    document.getElementById('invoiceModal').classList.remove('show');
}

function downloadInvoice(invoiceId) {
    showNotification(`Downloading invoice ${invoiceId}...`, 'info');
    // Simulate download
    setTimeout(() => {
        showNotification(`Invoice ${invoiceId} downloaded successfully!`, 'success');
    }, 2000);
}

function retryPayment(invoiceId) {
    if (confirm('Retry payment for this invoice?')) {
        showNotification('Redirecting to payment...', 'info');
        // Simulate payment retry
        setTimeout(() => {
            showNotification('Payment processed successfully!', 'success');
            loadBillingData();
        }, 3000);
    }
}

function exportBillingHistory() {
    showNotification('Exporting billing history...', 'info');
    // Simulate export
    setTimeout(() => {
        showNotification('Billing history exported successfully!', 'success');
    }, 2000);
}

function addPaymentMethod() {
    showNotification('Redirecting to add payment method...', 'info');
    // Redirect to payment method setup
}

function setDefaultPayment(methodId) {
    showNotification('Setting as default payment method...', 'info');
    setTimeout(() => {
        showNotification('Default payment method updated!', 'success');
        loadPaymentMethods();
    }, 1500);
}

function editPaymentMethod(methodId) {
    showNotification('Redirecting to edit payment method...', 'info');
}

function deletePaymentMethod(methodId) {
    if (confirm('Are you sure you want to delete this payment method?')) {
        showNotification('Deleting payment method...', 'info');
        setTimeout(() => {
            showNotification('Payment method deleted successfully!', 'success');
            loadPaymentMethods();
        }, 1500);
    }
}

function cancelSubscription() {
    if (confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your current billing period.')) {
        showNotification('Subscription cancellation requested. You will receive a confirmation email shortly.', 'info');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3685fb',
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
        zIndex: '1003',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        maxWidth: '400px'
    });
    
    const closeBtn = notification.querySelector('button');
    Object.assign(closeBtn.style, {
        background: 'none',
        border: 'none',
        color: 'white',
        fontSize: '1.25rem',
        cursor: 'pointer',
        padding: '0'
    });
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Close modal when clicking outside
document.getElementById('invoiceModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeInvoiceModal();
    }
});
</script>

<?php get_footer(); ?>