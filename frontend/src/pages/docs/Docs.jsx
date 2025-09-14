import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Skeleton } from '../../components/ui/skeleton';
import { toast } from 'sonner';

export default function Docs() {
  const [md, setMd] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true); setError('');
      try {
        const res = await fetch('/contracts.md');
        if (!res.ok) throw new Error('contracts.md not found');
        const text = await res.text();
        setMd(text);
      } catch (e) {
        setError(e.message || 'Failed to load docs');
        toast.error(e.message || 'Failed to load docs');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return (<div className="container mx-auto px-4 py-8 max-w-4xl"><Skeleton className="h-8 w-48 mb-4" /><Skeleton className="h-96 w-full" /></div>);

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Integration Contracts</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="text-red-600">{error}</div>
          ) : (
            <article className="prose prose-slate max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>
            </article>
          )}
        </CardContent>
      </Card>
    </div>
  );
}