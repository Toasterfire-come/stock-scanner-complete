import React, { useEffect, useState } from 'react';
import { endpoints } from '../../lib/api';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { toast } from 'sonner';
import { User, Lock, Bell, CreditCard, Download } from 'lucide-react';

const profileSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email(),
  phone: z.string().optional(),
  company: z.string().optional(),
});

const passwordSchema = z.object({
  current_password: z.string().min(1),
  new_password: z.string().min(8, 'Min 8 characters'),
  confirm_password: z.string().min(8),
}).refine((v) => v.new_password === v.confirm_password, { message: 'Passwords do not match', path: ['confirm_password'] });

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [history, setHistory] = useState({ items: [], page: 1, total: 0 });
  const [stats, setStats] = useState(null);

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm({ resolver: zodResolver(profileSchema) });
  const pwdForm = useForm({ resolver: zodResolver(passwordSchema) });

  useEffect(() => {
    const load = async () => {
      setLoading(true); setError('');
      const [p, bh, bs] = await Promise.all([
        endpoints.user.profileGet(),
        endpoints.user.billingHistory({ page: 1, limit: 10 }),
        endpoints.billing.stats(),
      ]);
      if (!p.ok) setError(p.error || 'Failed to load profile');
      if (p.ok) reset(p.data?.data || {});
      setHistory({ items: (bh.ok && (bh.data?.data || [])) || [], page: 1, total: (bh.ok && bh.data?.pagination?.total) || 0 });
      if (bs.ok) setStats(bs.data?.data || null);
      setLoading(false);
    };
    load();
  }, [reset]);

  const onSubmitProfile = async (values) => {
    const res = await endpoints.user.profileUpdate(values);
    if (!res.ok) return toast.error(res.error || 'Update failed');
    toast.success('Profile updated');
  };

  const onChangePassword = async (values) => {
    const res = await endpoints.user.changePassword(values);
    if (!res.ok) return toast.error(res.error || 'Password change failed');
    toast.success('Password updated');
    pwdForm.reset();
  };

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-8">
      <h1 className="text-xl font-semibold">Account</h1>

      {loading && <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-muted animate-pulse rounded" />)}</div>}
      {error && <div className="p-4 border rounded bg-destructive/10 text-destructive">{error}</div>}

      {!loading && !error && (
        <>
          {/* Profile */}
          <section className="p-4 border rounded space-y-3">
            <div className="flex items-center gap-2"><User className="h-4 w-4" /><h2 className="font-medium">Profile</h2></div>
            <form onSubmit={handleSubmit(onSubmitProfile)} className="grid md:grid-cols-2 gap-3">
              <div>
                <label className="text-sm">First name</label>
                <input className="mt-1 w-full px-3 py-2 border rounded" {...register('first_name')} />
                {errors.first_name && <p className="text-xs text-red-600">{errors.first_name.message}</p>}
              </div>
              <div>
                <label className="text-sm">Last name</label>
                <input className="mt-1 w-full px-3 py-2 border rounded" {...register('last_name')} />
                {errors.last_name && <p className="text-xs text-red-600">{errors.last_name.message}</p>}
              </div>
              <div>
                <label className="text-sm">Email</label>
                <input className="mt-1 w-full px-3 py-2 border rounded" {...register('email')} />
                {errors.email && <p className="text-xs text-red-600">{errors.email.message}</p>}
              </div>
              <div>
                <label className="text-sm">Phone</label>
                <input className="mt-1 w-full px-3 py-2 border rounded" {...register('phone')} />
              </div>
              <div className="md:col-span-2">
                <label className="text-sm">Company</label>
                <input className="mt-1 w-full px-3 py-2 border rounded" {...register('company')} />
              </div>
              <div className="md:col-span-2">
                <button disabled={isSubmitting} className="px-3 py-2 rounded bg-primary text-primary-foreground">{isSubmitting ? 'Saving...' : 'Save changes'}</button>
              </div>
            </form>
          </section>

          {/* Password */}
          <section className="p-4 border rounded space-y-3">
            <div className="flex items-center gap-2"><Lock className="h-4 w-4" /><h2 className="font-medium">Change Password</h2></div>
            <form onSubmit={pwdForm.handleSubmit(onChangePassword)} className="grid md:grid-cols-3 gap-3">
              <div>
                <label className="text-sm">Current password</label>
                <input type="password" className="mt-1 w-full px-3 py-2 border rounded" {...pwdForm.register('current_password')} />
                {pwdForm.formState.errors.current_password && <p className="text-xs text-red-600">{pwdForm.formState.errors.current_password.message}</p>}
              </div>
              <div>
                <label className="text-sm">New password</label>
                <input type="password" className="mt-1 w-full px-3 py-2 border rounded" {...pwdForm.register('new_password')} />
                {pwdForm.formState.errors.new_password && <p className="text-xs text-red-600">{pwdForm.formState.errors.new_password.message}</p>}
              </div>
              <div>
                <label className="text-sm">Confirm password</label>
                <input type="password" className="mt-1 w-full px-3 py-2 border rounded" {...pwdForm.register('confirm_password')} />
                {pwdForm.formState.errors.confirm_password && <p className="text-xs text-red-600">{pwdForm.formState.errors.confirm_password.message}</p>}
              </div>
              <div className="md:col-span-3">
                <button disabled={pwdForm.formState.isSubmitting} className="px-3 py-2 rounded bg-primary text-primary-foreground">{pwdForm.formState.isSubmitting ? 'Updating...' : 'Update password'}</button>
              </div>
            </form>
          </section>

          {/* Notifications */}
          <Notifications />

          {/* Billing */}
          <Billing history={history} stats={stats} />
        </>
      )}
    </div>
  );
}

function Notifications() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [settings, setSettings] = useState({ trading: {}, portfolio: {}, news: {}, security: {} });

  useEffect(() => {
    const load = async () => {
      setLoading(true); setError('');
      const res = await endpoints.user.notificationGet();
      if (!res.ok) setError(res.error || 'Failed to load notification settings');
      else setSettings(res.data?.data || res.data || settings);
      setLoading(false);
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggle = (group, key) => setSettings((s) => ({ ...s, [group]: { ...s[group], [key]: !s[group]?.[key] } }));

  const save = async () => {
    const res = await endpoints.user.notificationUpdate(settings);
    if (!res.ok) return toast.error(res.error || 'Failed to save');
    toast.success('Notification settings saved');
  };

  if (loading) return <div className="h-24 bg-muted animate-pulse rounded" />;
  if (error) return <div className="p-4 border rounded bg-destructive/10 text-destructive">{error}</div>;

  return (
    <section className="p-4 border rounded space-y-3">
      <div className="flex items-center gap-2"><Bell className="h-4 w-4" /><h2 className="font-medium">Notification Settings</h2></div>
      <div className="grid md:grid-cols-2 gap-4">
        {Object.entries(settings).map(([group, cfg]) => (
          <div key={group} className="p-3 border rounded">
            <div className="font-medium capitalize mb-2">{group}</div>
            <div className="space-y-1">
              {Object.keys(cfg || {}).length ? Object.entries(cfg).map(([k, v]) => (
                <label key={k} className="flex items-center gap-2">
                  <input type="checkbox" checked={!!v} onChange={() => toggle(group, k)} />
                  <span className="text-sm capitalize">{k.replaceAll('_', ' ')}</span>
                </label>
              )) : <div className="text-sm text-muted-foreground">No settings found</div>}
            </div>
          </div>
        ))}
      </div>
      <button onClick={save} className="px-3 py-2 rounded bg-primary text-primary-foreground">Save settings</button>
    </section>
  );
}

function Billing({ history, stats }) {
  return (
    <section className="p-4 border rounded space-y-4">
      <div className="flex items-center gap-2"><CreditCard className="h-4 w-4" /><h2 className="font-medium">Billing</h2></div>
      {stats ? (
        <div className="grid md:grid-cols-4 gap-3">
          <BillMetric label="Total Spent" value={`$${(stats.total_spent ?? 0).toLocaleString()}`} />
          <BillMetric label="Recent Payments" value={stats.recent_payments ?? '-'} />
          <BillMetric label="Account Status" value={stats.account_status ?? '-'} />
          <BillMetric label="Next Billing" value={formatDate(stats.next_billing_date)} />
        </div>
      ) : (
        <div className="h-14 bg-muted animate-pulse rounded" />
      )}

      <div className="overflow-x-auto border rounded">
        <table className="min-w-full text-sm">
          <thead className="bg-muted text-muted-foreground">
            <tr>
              <th className="text-left p-2">Date</th>
              <th className="text-left p-2">Description</th>
              <th className="text-left p-2">Amount</th>
              <th className="text-left p-2">Status</th>
              <th className="text-left p-2">Method</th>
              <th className="text-left p-2">Invoice</th>
            </tr>
          </thead>
          <tbody>
            {history.items.map((i) => (
              <tr key={i.id} className="border-t">
                <td className="p-2 whitespace-nowrap">{i.date}</td>
                <td className="p-2">{i.description}</td>
                <td className="p-2">${i.amount?.toLocaleString?.() ?? i.amount}</td>
                <td className="p-2">{i.status}</td>
                <td className="p-2">{i.method}</td>
                <td className="p-2">
                  {i.download_url ? (
                    <a href={i.download_url} className="inline-flex items-center gap-1 text-primary hover:underline">
                      <Download className="h-4 w-4" /> Download
                    </a>
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </td>
              </tr>
            ))}
            {!history.items.length && (
              <tr>
                <td className="p-4 text-center text-muted-foreground" colSpan={6}>No billing history</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function BillMetric({ label, value }) {
  return (
    <div className="p-3 border rounded">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}

function formatDate(str) {
  if (!str) return '-';
  try { return new Date(str).toLocaleString(); } catch { return str; }
}