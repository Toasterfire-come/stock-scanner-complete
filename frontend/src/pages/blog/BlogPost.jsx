import React, { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SEO from "../../components/SEO";
import { Card, CardContent } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Loader2, ArrowLeft } from "lucide-react";
import { getPostBySlug } from "./blogPosts";

export default function BlogPost() {
  const { slug } = useParams();
  const post = useMemo(() => getPostBySlug(slug), [slug]);

  const [markdown, setMarkdown] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        if (!post) {
          setError("Post not found");
          return;
        }
        const res = await fetch(post.mdPath);
        if (!res.ok) throw new Error(`Failed to load post`);
        const text = await res.text();
        if (mounted) setMarkdown(text);
      } catch (e) {
        if (mounted) setError(e?.message || "Failed to load post");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    run();
    return () => { mounted = false; };
  }, [post]);

  if (!post) {
    return (
      <div className="container mx-auto px-4 py-10 max-w-3xl">
        <SEO title="Post not found | Trade Scan Pro" robots="noindex" />
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="text-xl font-semibold">Post not found</div>
            <Link to="/blog">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to blog
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-10 max-w-3xl">
      <SEO title={`${post.title} | Trade Scan Pro`} description={post.description} />

      <div className="mb-6">
        <Link to="/blog">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to blog
          </Button>
        </Link>
      </div>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{post.title}</h1>
        <div className="flex flex-wrap items-center gap-2 mt-3">
          <div className="text-sm text-gray-500">{new Date(post.date).toLocaleDateString()}</div>
          {(post.tags || []).map((t) => (
            <Badge key={t} variant="outline">
              {t}
            </Badge>
          ))}
        </div>
        {post.description && <p className="text-gray-600 mt-4">{post.description}</p>}
      </div>

      <Card>
        <CardContent className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12 text-gray-500">
              <Loader2 className="h-6 w-6 mr-2 animate-spin" />
              Loading…
            </div>
          ) : error ? (
            <div className="text-red-600">{error}</div>
          ) : (
            <article className="prose prose-slate max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
            </article>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

