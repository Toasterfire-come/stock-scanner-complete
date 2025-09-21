import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../components/ui/select';
import { Switch } from '../../../components/ui/switch';
import { Badge } from '../../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../components/ui/dialog';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { 
  Calendar, 
  Clock, 
  Plus, 
  Play, 
  Pause, 
  Trash2, 
  Edit,
  Download,
  Mail,
  Settings,
  CheckCircle,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../../../context/SecureAuthContext';
import { toast } from 'sonner';

const ScheduledExports = () => {
  const { user } = useAuth();
  const [schedules, setSchedules] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    description: '',
    export_type: 'portfolio',
    format: 'csv',
    frequency: 'weekly',
    time: '09:00',
    timezone: 'UTC',
    enabled: true,
    email_notifications: true,
    email_recipients: '',
    retention_days: 30
  });

  useEffect(() => {
    loadScheduledExports();
  }, []);

  const loadScheduledExports = async () => {
    // Mock scheduled exports data
    const mockSchedules = [
      {
        id: 1,
        name: 'Weekly Portfolio Report',
        description: 'Comprehensive portfolio performance report sent every Monday',
        export_type: 'portfolio',
        format: 'pdf',
        frequency: 'weekly',
        time: '09:00',
        timezone: 'UTC',
        enabled: true,
        email_notifications: true,
        email_recipients: 'investor@company.com',
        retention_days: 30,
        last_run: '2024-01-15T09:00:00Z',
        next_run: '2024-01-22T09:00:00Z',
        status: 'active',
        run_count: 12
      },
      {
        id: 2,
        name: 'Monthly Stock Analysis',
        description: 'Detailed stock analysis for all holdings',
        export_type: 'stocks',
        format: 'xlsx',
        frequency: 'monthly',
        time: '08:00',
        timezone: 'UTC',
        enabled: false,
        email_notifications: false,
        email_recipients: '',
        retention_days: 60,
        last_run: '2024-01-01T08:00:00Z',
        next_run: null,
        status: 'paused',
        run_count: 3
      }
    ];
    setSchedules(mockSchedules);
  };

  const handleCreateSchedule = async () => {
    if (!newSchedule.name.trim()) {
      toast.error('Please enter a schedule name');
      return;
    }

    setLoading(true);
    try {
      // Mock API call - in real app this would call the backend
      const schedule = {
        ...newSchedule,
        id: Date.now(),
        status: 'active',
        run_count: 0,
        last_run: null,
        next_run: calculateNextRun(newSchedule.frequency, newSchedule.time)
      };

      setSchedules(prev => [...prev, schedule]);
      setShowCreateDialog(false);
      setNewSchedule({
        name: '',
        description: '',
        export_type: 'portfolio',
        format: 'csv',
        frequency: 'weekly',
        time: '09:00',
        timezone: 'UTC',
        enabled: true,
        email_notifications: true,
        email_recipients: '',
        retention_days: 30
      });
      toast.success('Scheduled export created successfully');
    } catch (error) {
      console.error('Failed to create scheduled export:', error);
      toast.error('Failed to create scheduled export');
    } finally {
      setLoading(false);
    }
  };

  const toggleSchedule = async (id) => {
    setSchedules(prev => prev.map(schedule => 
      schedule.id === id 
        ? { 
            ...schedule, 
            enabled: !schedule.enabled,
            status: !schedule.enabled ? 'active' : 'paused',
            next_run: !schedule.enabled ? calculateNextRun(schedule.frequency, schedule.time) : null
          }
        : schedule
    ));
    toast.success('Schedule updated');
  };

  const deleteSchedule = async (id) => {
    setSchedules(prev => prev.filter(schedule => schedule.id !== id));
    toast.success('Scheduled export deleted');
  };

  const runNow = async (schedule) => {
    toast.success(`Running ${schedule.name}... Check your export history for results.`);
    // Update last run time
    setSchedules(prev => prev.map(s => 
      s.id === schedule.id 
        ? { 
            ...s, 
            last_run: new Date().toISOString(),
            run_count: s.run_count + 1
          }
        : s
    ));
  };

  const calculateNextRun = (frequency, time) => {
    const now = new Date();
    const [hours, minutes] = time.split(':').map(Number);
    
    let nextRun = new Date();
    nextRun.setHours(hours, minutes, 0, 0);
    
    switch (frequency) {
      case 'daily':
        if (nextRun <= now) {
          nextRun.setDate(nextRun.getDate() + 1);
        }
        break;
      case 'weekly':
        nextRun.setDate(nextRun.getDate() + (7 - nextRun.getDay() + 1) % 7);
        if (nextRun <= now) {
          nextRun.setDate(nextRun.getDate() + 7);
        }
        break;
      case 'monthly':
        nextRun.setMonth(nextRun.getMonth() + 1, 1);
        break;
      default:
        break;
    }
    
    return nextRun.toISOString();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4" />;
      case 'paused':
        return <Pause className="h-4 w-4" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Scheduled Exports</h1>
              <p className="text-gray-600">Automate your data exports with custom schedules and notifications</p>
            </div>
            <Button 
              onClick={() => setShowCreateDialog(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Schedule
            </Button>
          </div>
        </div>

        {/* Scheduled Exports List */}
        <div className="space-y-6">
          {schedules.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Scheduled Exports</h3>
                <p className="text-gray-600 mb-4">Create your first scheduled export to automate data delivery.</p>
                <Button 
                  onClick={() => setShowCreateDialog(true)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create Schedule
                </Button>
              </CardContent>
            </Card>
          ) : (
            schedules.map((schedule) => (
              <Card key={schedule.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{schedule.name}</h3>
                        <Badge className={`text-xs ${getStatusColor(schedule.status)}`}>
                          <div className="flex items-center gap-1">
                            {getStatusIcon(schedule.status)}
                            {schedule.status}
                          </div>
                        </Badge>
                        <Switch
                          checked={schedule.enabled}
                          onCheckedChange={() => toggleSchedule(schedule.id)}
                        />
                      </div>
                      
                      <p className="text-gray-600 mb-4">{schedule.description}</p>

                      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Type:</span>
                          <div className="font-medium capitalize">{schedule.export_type} ({schedule.format.toUpperCase()})</div>
                        </div>
                        
                        <div>
                          <span className="text-gray-500">Frequency:</span>
                          <div className="font-medium capitalize">{schedule.frequency} at {schedule.time}</div>
                        </div>
                        
                        <div>
                          <span className="text-gray-500">Last Run:</span>
                          <div className="font-medium">{formatDate(schedule.last_run)}</div>
                        </div>
                        
                        <div>
                          <span className="text-gray-500">Next Run:</span>
                          <div className="font-medium">{formatDate(schedule.next_run)}</div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 mt-4 text-sm text-gray-600">
                        <span>Runs: {schedule.run_count}</span>
                        {schedule.email_notifications && (
                          <span className="flex items-center gap-1">
                            <Mail className="h-4 w-4" />
                            Email notifications enabled
                          </span>
                        )}
                        <span>Retention: {schedule.retention_days} days</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => runNow(schedule)}
                        disabled={!schedule.enabled}
                      >
                        <Play className="h-4 w-4 mr-1" />
                        Run Now
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingSchedule(schedule);
                          setShowCreateDialog(true);
                        }}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => deleteSchedule(schedule.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Information Cards */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Schedule Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Maximum schedules:</span>
                <span className="font-medium">10</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Minimum frequency:</span>
                <span className="font-medium">Daily</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Maximum retention:</span>
                <span className="font-medium">90 days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Email notifications:</span>
                <span className="font-medium">Included</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Execution Times
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm text-gray-600">
                <p className="mb-2">All scheduled exports run in UTC timezone.</p>
                <ul className="space-y-1">
                  <li>• Daily: Every day at specified time</li>
                  <li>• Weekly: Every Monday at specified time</li>
                  <li>• Monthly: 1st of each month at specified time</li>
                  <li>• Quarterly: 1st of Jan, Apr, Jul, Oct</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Create/Edit Schedule Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingSchedule ? 'Edit Scheduled Export' : 'Create Scheduled Export'}
              </DialogTitle>
              <DialogDescription>
                Set up an automated export that runs on a regular schedule
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-6 py-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Schedule Name *</Label>
                  <Input
                    id="name"
                    value={newSchedule.name}
                    onChange={(e) => setNewSchedule(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Weekly Portfolio Report"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="export_type">Export Type</Label>
                  <Select 
                    value={newSchedule.export_type} 
                    onValueChange={(value) => setNewSchedule(prev => ({ ...prev, export_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="portfolio">Portfolio Holdings</SelectItem>
                      <SelectItem value="stocks">Stocks Data</SelectItem>
                      <SelectItem value="watchlist">Watchlists</SelectItem>
                      <SelectItem value="alerts">Alerts History</SelectItem>
                      <SelectItem value="custom_report">Custom Report</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={newSchedule.description}
                  onChange={(e) => setNewSchedule(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Comprehensive portfolio performance report"
                />
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="frequency">Frequency</Label>
                  <Select 
                    value={newSchedule.frequency} 
                    onValueChange={(value) => setNewSchedule(prev => ({ ...prev, frequency: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="quarterly">Quarterly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="time">Time (UTC)</Label>
                  <Input
                    id="time"
                    type="time"
                    value={newSchedule.time}
                    onChange={(e) => setNewSchedule(prev => ({ ...prev, time: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="format">Format</Label>
                  <Select 
                    value={newSchedule.format} 
                    onValueChange={(value) => setNewSchedule(prev => ({ ...prev, format: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="csv">CSV</SelectItem>
                      <SelectItem value="xlsx">Excel</SelectItem>
                      <SelectItem value="pdf">PDF</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-base font-medium">Email Notifications</Label>
                    <p className="text-sm text-gray-600">Send email when export completes</p>
                  </div>
                  <Switch
                    checked={newSchedule.email_notifications}
                    onCheckedChange={(checked) => setNewSchedule(prev => ({ ...prev, email_notifications: checked }))}
                  />
                </div>

                {newSchedule.email_notifications && (
                  <div className="space-y-2">
                    <Label htmlFor="email_recipients">Email Recipients</Label>
                    <Input
                      id="email_recipients"
                      value={newSchedule.email_recipients}
                      onChange={(e) => setNewSchedule(prev => ({ ...prev, email_recipients: e.target.value }))}
                      placeholder="email1@company.com, email2@company.com"
                    />
                    <p className="text-xs text-gray-600">Separate multiple emails with commas</p>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="retention_days">File Retention (Days)</Label>
                  <Select 
                    value={newSchedule.retention_days.toString()} 
                    onValueChange={(value) => setNewSchedule(prev => ({ ...prev, retention_days: parseInt(value) }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7">7 days</SelectItem>
                      <SelectItem value="30">30 days</SelectItem>
                      <SelectItem value="60">60 days</SelectItem>
                      <SelectItem value="90">90 days</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateSchedule}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  editingSchedule ? 'Update Schedule' : 'Create Schedule'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default ScheduledExports;