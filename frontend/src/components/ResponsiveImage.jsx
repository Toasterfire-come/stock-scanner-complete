import React from "react";
import { cn } from "../lib/utils";

export default function ResponsiveImage({
  src,
  alt = "",
  className,
  width,
  height,
  sources = [],
  loading = "lazy",
  decoding = "async",
  sizes = "(max-width: 768px) 100vw, 768px",
  ...rest
}) {
  // sources: [{ srcSet: 'image.avif 1x, image@2x.avif 2x', type: 'image/avif' }, { srcSet: 'image.webp 1x, image@2x.webp 2x', type: 'image/webp' }]
  return (
    <picture>
      {sources.map(({ srcSet, type }) => (
        <source key={type + srcSet} srcSet={srcSet} type={type} sizes={sizes} />
      ))}
      <img
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={loading}
        decoding={decoding}
        className={cn("block", className)}
        {...rest}
      />
    </picture>
  );
}

