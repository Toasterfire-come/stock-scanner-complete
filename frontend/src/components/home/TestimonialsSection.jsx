import React from "react";
import { Card, CardContent } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Star, TrendingUp } from "lucide-react";

const TestimonialsSection = ({ testimonials = [] }) => {
  return (
    <section className="py-16 sm:py-24 bg-white" id="testimonials">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12 sm:mb-20">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4 sm:mb-6">
            Success Stories From Our Traders
          </h2>
          <p className="text-xl sm:text-2xl text-gray-600">
            Real results from real traders using Trade Scan Pro
          </p>
        </div>
        <div className="grid lg:grid-cols-3 gap-6 sm:gap-8">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="hover:shadow-2xl transition-shadow duration-300 border-t-4 border-t-green-500">
              <CardContent className="p-6 sm:p-8">
                <div className="flex mb-4 sm:mb-6">
                  {[...Array(testimonial.rating || 5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 sm:h-6 sm:w-6 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-base sm:text-lg text-gray-700 mb-4 sm:mb-6 leading-relaxed">
                  "{testimonial.content}"
                </blockquote>
                <div className="border-t pt-4 sm:pt-6">
                  <div className="font-bold text-lg sm:text-xl text-gray-900">{testimonial.name}</div>
                  <div className="text-gray-600 mb-2">{testimonial.role}</div>
                  {testimonial.company && (
                    <div className="text-sm text-gray-500 mb-3">{testimonial.company}</div>
                  )}
                  {testimonial.profit && (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      {testimonial.profit}
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;

