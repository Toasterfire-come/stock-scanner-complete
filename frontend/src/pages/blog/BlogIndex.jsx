import React from "react";
import { Link } from "react-router-dom";
import SEO from "../../components/SEO";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { BLOG_POSTS } from "./blogPosts";

export default function BlogIndex() {
  const posts = [...BLOG_POSTS].sort((a, b) => (a.date < b.date ? 1 : -1));

  return (
    <div className="container mx-auto px-4 py-10 max-w-5xl">
      <SEO
        title="Blog | Trade Scan Pro"
        description="Trading education, backtesting guides, and product updates from Trade Scan Pro."
      />

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Blog</h1>
        <p className="text-gray-600 mt-2">
          Practical guides on backtesting, metrics, and building better strategies.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {posts.map((p) => (
          <Link key={p.slug} to={`/blog/${p.slug}`} className="block">
            <Card className="hover:shadow-md transition-shadow h-full">
              <CardHeader>
                <CardTitle>{p.title}</CardTitle>
                <CardDescription>{p.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-4">
                <div className="text-xs text-gray-500">{new Date(p.date).toLocaleDateString()}</div>
                <div className="flex flex-wrap gap-2 justify-end">
                  {(p.tags || []).slice(0, 3).map((t) => (
                    <Badge key={t} variant="outline">
                      {t}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

