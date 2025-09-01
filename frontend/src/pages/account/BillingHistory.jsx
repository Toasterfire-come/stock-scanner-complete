import React, { useState, useEffect } from "react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Skeleton } from "../../components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { toast } from "sonner";
import { 
  Download, 
  CreditCard, 
  Calendar, 
  DollarSign, 
  FileText,
  Filter,
  ArrowUpRight,
  CheckCircle,
  XCircle,
  Clock
} from "lucide-react";
import { getBillingHistory, downloadInvoice, getBillingStats } from "../../api/client";

const BillingHistory = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [billingHistory, setBillingHistory] = useState([]);
  const [billingStats, setBillingStats] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("all");
  const [downloadingIds, setDownloadingIds] = useState(new Set());

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [historyResponse, statsResponse] = await Promise.all([
          getBillingHistory({ page: currentPage, limit: 10 }),
          getBillingStats()
        ]);

        if (historyResponse.success) {
          setBillingHistory(historyResponse.data);
        }

        if (statsResponse.success) {
          setBillingStats(statsResponse.data);
        }
      } catch (error) {
        console.error("Failed to load billing data:", error);
        // Mock data for demo
        setBillingHistory([
          {
            id: "inv_001",
            date: "2024-03-15",
            description: "Stock Scanner Professional - Monthly",
            amount: 29.00,
            status: "paid",
            method: "Credit Card",
            download_url: "/api/billing/download/inv_001/"
          },
          {
            id: "inv_002", 
            date: "2024-02-15",
            description: "Stock Scanner Professional - Monthly",
            amount: 29.00,
            status: "paid",
            method: "Credit Card",
            download_url: "/api/billing/download/inv_002/"
          },
          {
            id: "inv_003",
            date: "2024-01-15",
            description: "Stock Scanner Professional - Monthly",
            amount: 29.00,
            status: "failed",
            method: "Credit Card",
            download_url: null
          }
        ]);
        setBillingStats({
          total_spent: 87.00,
          recent_payments: 2,
          account_status: "active",
          next_billing_date: "2024-04-15T00:00:00Z"
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [currentPage]);

  const handleDownloadInvoice = async (invoiceId) => {
    setDownloadingIds(prev => new Set(prev.add(invoiceId)));
    
    try {
      const blob = await downloadInvoice(invoiceId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success("Invoice downloaded successfully");
    } catch (error) {
      toast.error("Failed to download invoice");
    } finally {
      setDownloadingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(invoiceId);
        return newSet;
      });
    }
  };

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'paid':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      paid: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800", 
      pending: "bg-yellow-100 text-yellow-800",
      refunded: "bg-blue-100 text-blue-800"
    };
    
    return (
      <Badge className={variants[status.toLowerCase()] || "bg-gray-100 text-gray-800"}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const filteredHistory = billingHistory.filter(item => 
    statusFilter === "all" || item.status.toLowerCase() === statusFilter
  );

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </CardContent>
              </Card>
            ))}
          </div>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Billing History</h1>
          <p className="text-gray-600 mt-2">
            View your billing history, download invoices, and manage payments
          </p>
        </div>

        {/* Billing Stats */}
        {billingStats && (
          <div className="grid md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <DollarSign className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <div className="text-2xl font-bold">${billingStats.total_spent}</div>
                    <div className="text-sm text-gray-600">Total Spent</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <CreditCard className="h-8 w-8 text-blue-500" />
                  <div className="ml-4">
                    <div className="text-2xl font-bold">{billingStats.recent_payments}</div>
                    <div className="text-sm text-gray-600">Recent Payments</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <CheckCircle className="h-8 w-8 text-green-500" />
                  <div className="ml-4">
                    <div className="text-2xl font-bold capitalize">{billingStats.account_status}</div>
                    <div className="text-sm text-gray-600">Account Status</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <Calendar className="h-8 w-8 text-purple-500" />
                  <div className="ml-4">
                    <div className="text-2xl font-bold">
                      {new Date(billingStats.next_billing_date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                    <div className="text-sm text-gray-600">Next Billing</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Billing History */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2" />
                  Payment History
                </CardTitle>
                <CardDescription>
                  All your billing transactions and invoices
                </CardDescription>
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="paid">Paid</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="refunded">Refunded</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            {filteredHistory.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No billing history</h3>
                <p className="text-gray-600">
                  You haven't made any payments yet. Upgrade to a paid plan to get started.
                </p>
              </div>
            ) : (
              <div className="space-y-0 divide-y">
                {filteredHistory.map((item) => (
                  <div key={item.id} className="flex items-center justify-between py-4">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(item.status)}
                      <div>
                        <div className="font-medium">{item.description}</div>
                        <div className="text-sm text-gray-600 flex items-center space-x-2">
                          <span>{new Date(item.date).toLocaleDateString()}</span>
                          <span>•</span>
                          <span>{item.method}</span>
                          <span>•</span>
                          <span>Invoice #{item.id}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="font-semibold">${item.amount.toFixed(2)}</div>
                        {getStatusBadge(item.status)}
                      </div>
                      
                      {item.download_url && item.status === 'paid' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadInvoice(item.id)}
                          disabled={downloadingIds.has(item.id)}
                        >
                          {downloadingIds.has(item.id) ? (
                            "Downloading..."
                          ) : (
                            <>
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </>
                          )}
                        </Button>
                      )}

                      {item.status === 'failed' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toast.info("Retry payment functionality coming soon")}
                        >
                          <ArrowUpRight className="h-4 w-4 mr-2" />
                          Retry
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payment Method */}
        <Card>
          <CardHeader>
            <CardTitle>Payment Methods</CardTitle>
            <CardDescription>
              Manage your payment methods and billing information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <CreditCard className="h-6 w-6 text-gray-400" />
                <div>
                  <div className="font-medium">•••• •••• •••• 4242</div>
                  <div className="text-sm text-gray-600">Expires 12/2027</div>
                </div>
              </div>
              <Button variant="outline" size="sm">
                Update
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default BillingHistory;