import React from 'react';
import AutoSizer from 'react-virtualized-auto-sizer';
import { List } from 'react-window';

/**
 * Generic virtualized list wrapper using react-window + AutoSizer
 * Props:
 * - items: array
 * - itemSize: number (row height)
 * - row: ({ index, style, item }) => ReactNode
 * - height: optional fixed height; if not provided, uses AutoSizer parent's height
 */
export default function VirtualizedList({ items = [], itemSize = 48, row, height, className }) {
  const Row = ({ index, style }) => row({ index, style, item: items[index] });
  if (!items.length) return null;

  if (height) {
    return (
      <List
        className={className}
        height={height}
        itemCount={items.length}
        itemSize={itemSize}
        width="100%"
      >
        {Row}
      </List>
    );
  }

  return (
    <div style={{ height: 500 }} className={className}>
      <AutoSizer>
        {({ height: h, width }) => (
          <List height={h} width={width} itemSize={itemSize} itemCount={items.length}>
            {Row}
          </List>
        )}
      </AutoSizer>
    </div>
  );
}