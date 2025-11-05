import React from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { ArrowRight } from "lucide-react";
import { docsContent, categoriesMeta } from "./contentMap";

const DocsCategory = () => {
  const { category } = useParams();
  const meta = categoriesMeta[category];
  const items = docsContent[category];

  if (!meta || !items) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-3xl font-bold mb-4">Category Not Found</h1>
        <p className="text-gray-600">Return to the <Link className="underline" to="/docs">docs</Link>.</p>
      </div>
    );
  }

  const entries = Object.entries(items);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto">
            <Badge className={`mb-4 ${meta.badgeColor}`}>{meta.title}</Badge>
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">{meta.title}</h1>
            <p className="text-xl text-gray-700">{meta.description}</p>
          </div>
        </div>
      </section>

      <section className="py-8">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {entries.map(([slug, article]) => (
              <Card key={slug} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{article.title}</h3>
                    <span className="text-xs text-gray-500">{article.readTime}</span>
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{article.description}</p>
                  <Link to={`/docs/${category}/${slug}`} className="text-blue-600 hover:text-blue-700 inline-flex items-center text-sm">
                    Read Guide
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default DocsCategory;

