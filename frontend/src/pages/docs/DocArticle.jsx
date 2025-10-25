import React from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Alert, AlertDescription } from "../../components/ui/alert";
import {
  ArrowLeft,
  CheckCircle,
  Clock,
  BookOpen,
  ArrowRight,
  Lightbulb
} from "lucide-react";
import { docsContent, categoriesMeta } from "./contentMap";

const resolveIcon = (iconName) => {
  const map = { BookOpen };
  return map[iconName] || BookOpen;
};

const DocArticle = () => {
  const { category, slug } = useParams();
  const categoryContent = docsContent[category] || {};
  const article = categoryContent[slug];
  const meta = categoriesMeta[category];

  if (!article || !meta) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">Article Not Found</h1>
          <p className="text-gray-600 mb-6">We couldn't find the documentation you're looking for.</p>
          <Button asChild>
            <Link to="/docs">Back to Documentation</Link>
          </Button>
        </div>
      </div>
    );
  }

  const CategoryIcon = resolveIcon(meta.icon);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" asChild>
              <Link to="/docs">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Documentation
              </Link>
            </Button>
            <span className="text-gray-400">/</span>
            <Badge variant="outline">{meta.title}</Badge>
          </div>
        </div>
      </div>

      {/* Header */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <Badge className={`mb-4 ${meta.badgeColor}`}>
                <CategoryIcon className="h-4 w-4 mr-2" />
                {meta.title}
              </Badge>
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                {article.title}
              </h1>
              <p className="text-xl text-gray-700 leading-relaxed">
                {article.description}
              </p>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600 mb-8">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-2" />
                {article.readTime}
              </div>
              <div className="flex items-center">
                <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                {article.updated}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Body */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto space-y-8">
            {article.sections?.map((section, index) => (
              <Card key={index} className="overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
                  <CardTitle className="text-xl text-gray-900">{section.title}</CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  {section.text && (
                    <p className="text-gray-700 mb-4">{section.text}</p>
                  )}
                  {Array.isArray(section.bullets) && (
                    <ul className="space-y-3">
                      {section.bullets.map((item, i) => (
                        <li key={i} className="flex items-start">
                          <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            ))}

            {Array.isArray(article.related) && article.related.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Related Guides</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {article.related.map((rel, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="text-gray-800">{rel.title}</div>
                      <Button asChild variant="outline" size="sm">
                        <Link to={rel.link}>
                          Read
                          <ArrowRight className="h-4 w-4 ml-1" />
                        </Link>
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            <Alert className="border-blue-200 bg-blue-50">
              <Lightbulb className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <strong>Tip:</strong> Use the breadcrumb to navigate back to the main docs and explore more guides.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DocArticle;

