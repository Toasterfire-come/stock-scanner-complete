import React from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { endpoints } from '../../lib/api';
import { toast } from 'sonner';
import { useNavigate, Link } from 'react-router-dom';

const schema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

export default function Login() {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({ resolver: zodResolver(schema) });

  const onSubmit = async (values) => {
    const res = await endpoints.auth.login(values);
    if (!res.ok) return toast.error(res.error || 'Login failed');
    toast.success('Logged in');
    navigate('/onboarding');
  };

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-xl font-semibold mb-4">Login</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
        <div>
          <label className="text-sm">Username</label>
          <input className="mt-1 w-full px-3 py-2 border rounded" {...register('username')} />
          {errors.username && <p className="text-xs text-red-600">{errors.username.message}</p>}
        </div>
        <div>
          <label className="text-sm">Password</label>
          <input type="password" className="mt-1 w-full px-3 py-2 border rounded" {...register('password')} />
          {errors.password && <p className="text-xs text-red-600">{errors.password.message}</p>}
        </div>
        <button disabled={isSubmitting} className="w-full px-3 py-2 rounded bg-primary text-primary-foreground">{isSubmitting ? 'Signing in...' : 'Sign in'}</button>
      </form>
      <div className="text-sm text-muted-foreground mt-3">
        No account? <Link to="/auth/sign-up" className="text-primary hover:underline">Sign up</Link>
      </div>
    </div>
  );
}