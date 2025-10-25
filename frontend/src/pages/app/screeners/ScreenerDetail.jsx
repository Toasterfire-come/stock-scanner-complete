import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/card";
import { Alert, AlertDescription } from "../../../components/ui/alert";
import { Filter as FilterIcon, Edit, Copy, Download, Trash2, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { getScreener, runScreener, deleteScreener, createScreener, exportStocksCSV } from "../../../api/client";

const ScreenerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [screener, setScreener] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getScreener(id);
        setScreener(res?.data || null);
      } catch (e) {
        setError("Failed to load screener");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const handleRun = async () => {
    setBusy(true);
    try {
      const res = await runScreener(id);
      if (res?.success !== false) {
        toast.success("Screener ran successfully");
        navigate(`/app/screeners/${id}/results`);
      } else {
        throw new Error(res?.message || "Failed");
      }
    } catch (e) {
      toast.error("Failed to run screener");
    } finally {
      setBusy(false);
    }
  };

  const handleExport = async () => {
    setBusy(true);
    try {
      const csvData = await exportStocksCSV({ screener_id: id });
      const blob = new Blob([csvData], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `screener-results-${id}-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success("Export started");
    } catch (e) {
      toast.error("Failed to export results");
    } finally {
      setBusy(false);
    }
  };

  const handleDuplicate = async () => {
    if (!screener) return;
    setBusy(true);
    try {
      const res = await createScreener({
        name: `${screener.name} (Copy)`,
        description: screener.description,
        criteria: screener.criteria || [],
        is_public: false,
      });
      if (res?.success) {
        toast.success("Screener duplicated");
      } else {
        throw new Error(res?.message || "Failed");
      }
    } catch (e) {
      toast.error("Failed to duplicate");
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this screener?")) return;
    setBusy(true);
    try {
      const res = await deleteScreener(id);
      if (res?.success !== false) {
        toast.success("Screener deleted");
        navigate("/app/screeners");
      } else {
        throw new Error(res?.message || "Failed");
      }
    } catch (e) {
      toast.error("Failed to delete");
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Button variant="outline" asChild>
            <Link to="/app/screeners"><ArrowLeft className="h-4 w-4 mr-2" />Back</Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{screener?.name}</h1>
            <p className="text-gray-600 mt-1">{screener?.description || "No description provided"}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRun} disabled={busy}>
            <FilterIcon className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" asChild>
            <Link to={`/app/screeners/${id}/edit`}>
              <Edit className="h-4 w-4 mr-2" />Edit
            </Link>
          </Button>
          <Button variant="outline" onClick={handleDuplicate} disabled={busy}>
            <Copy className="h-4 w-4 mr-2" />Duplicate
          </Button>
          <Button variant="outline" onClick={handleExport} disabled={busy}>
            <Download className="h-4 w-4 mr-2" />Export
          </Button>
          <Button variant="outline" className="text-red-600 hover:text-red-700" onClick={handleDelete} disabled={busy}>
            <Trash2 className="h-4 w-4 mr-2" />Delete
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>About this Screener</CardTitle>
          <CardDescription>Basic information</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-500">Visibility</div>
              <div className="font-medium">{screener?.is_public ? "Public" : "Private"}</div>
            </div>
            <div>
              <div className="text-gray-500">Criteria Count</div>
              <div className="font-medium">{Array.isArray(screener?.criteria) ? screener.criteria.length : 0}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ScreenerDetail;

