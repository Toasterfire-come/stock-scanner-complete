<?php
/**
 * Chart and visualization functions
 *
 * @package StockScannerPro
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Generate Chart.js configuration for stock price chart
 */
function stock_scanner_generate_price_chart_config($ticker, $data, $options = array()) {
    $default_options = array(
        'type' => 'line',
        'height' => 300,
        'responsive' => true,
        'theme' => 'light',
        'show_volume' => false,
        'time_period' => '1d',
    );
    
    $options = wp_parse_args($options, $default_options);
    
    // Generate color scheme based on theme
    $colors = stock_scanner_get_chart_colors($options['theme']);
    
    $config = array(
        'type' => $options['type'],
        'data' => $data,
        'options' => array(
            'responsive' => true,
            'maintainAspectRatio' => false,
            'interaction' => array(
                'intersect' => false,
                'mode' => 'index',
            ),
            'plugins' => array(
                'title' => array(
                    'display' => true,
                    'text' => strtoupper($ticker) . ' - Price Chart',
                    'font' => array(
                        'size' => 16,
                        'weight' => '600',
                    ),
                    'color' => $colors['text'],
                ),
                'legend' => array(
                    'display' => false,
                ),
                'tooltip' => array(
                    'backgroundColor' => $colors['tooltip_bg'],
                    'titleColor' => $colors['text'],
                    'bodyColor' => $colors['text'],
                    'borderColor' => $colors['border'],
                    'borderWidth' => 1,
                    'cornerRadius' => 6,
                    'displayColors' => false,
                    'callbacks' => array(
                        'label' => "function(context) {
                            return '$' + context.parsed.y.toFixed(2);
                        }",
                    ),
                ),
            ),
            'scales' => array(
                'x' => array(
                    'display' => true,
                    'grid' => array(
                        'display' => true,
                        'color' => $colors['grid'],
                    ),
                    'ticks' => array(
                        'color' => $colors['text_muted'],
                        'font' => array(
                            'size' => 11,
                        ),
                    ),
                ),
                'y' => array(
                    'display' => true,
                    'position' => 'right',
                    'grid' => array(
                        'display' => true,
                        'color' => $colors['grid'],
                    ),
                    'ticks' => array(
                        'color' => $colors['text_muted'],
                        'font' => array(
                            'size' => 11,
                        ),
                        'callback' => "function(value) {
                            return '$' + value.toFixed(2);
                        }",
                    ),
                ),
            ),
            'elements' => array(
                'point' => array(
                    'radius' => 0,
                    'hoverRadius' => 4,
                    'hitRadius' => 10,
                ),
                'line' => array(
                    'tension' => 0.4,
                    'borderWidth' => 2,
                ),
            ),
        ),
    );
    
    // Add volume chart if requested
    if ($options['show_volume'] && isset($data['volume_data'])) {
        $config['options']['scales']['volume'] = array(
            'type' => 'linear',
            'display' => false,
            'position' => 'right',
        );
    }
    
    return $config;
}

/**
 * Get chart color scheme
 */
function stock_scanner_get_chart_colors($theme = 'light') {
    if ($theme === 'dark') {
        return array(
            'primary' => '#3b82f6',
            'success' => '#10b981',
            'danger' => '#ef4444',
            'text' => '#f9fafb',
            'text_muted' => '#9ca3af',
            'background' => '#1f2937',
            'grid' => '#374151',
            'border' => '#4b5563',
            'tooltip_bg' => '#374151',
        );
    }
    
    return array(
        'primary' => '#3b82f6',
        'success' => '#10b981',
        'danger' => '#ef4444',
        'text' => '#1f2937',
        'text_muted' => '#6b7280',
        'background' => '#ffffff',
        'grid' => '#e5e7eb',
        'border' => '#d1d5db',
        'tooltip_bg' => '#ffffff',
    );
}

/**
 * Generate portfolio performance chart
 */
function stock_scanner_generate_portfolio_chart($portfolio_data) {
    $labels = array();
    $values = array();
    
    if (!empty($portfolio_data) && is_array($portfolio_data)) {
        foreach ($portfolio_data as $holding) {
            if (isset($holding['ticker']) && isset($holding['market_value'])) {
                $labels[] = strtoupper($holding['ticker']);
                $values[] = floatval($holding['market_value']);
            }
        }
    }
    
    $colors = stock_scanner_generate_color_palette(count($labels));
    
    return array(
        'type' => 'doughnut',
        'data' => array(
            'labels' => $labels,
            'datasets' => array(
                array(
                    'data' => $values,
                    'backgroundColor' => $colors['backgrounds'],
                    'borderColor' => $colors['borders'],
                    'borderWidth' => 2,
                    'hoverOffset' => 4,
                ),
            ),
        ),
        'options' => array(
            'responsive' => true,
            'maintainAspectRatio' => false,
            'plugins' => array(
                'title' => array(
                    'display' => true,
                    'text' => 'Portfolio Allocation',
                    'font' => array(
                        'size' => 16,
                        'weight' => '600',
                    ),
                ),
                'legend' => array(
                    'position' => 'bottom',
                    'labels' => array(
                        'usePointStyle' => true,
                        'padding' => 15,
                    ),
                ),
                'tooltip' => array(
                    'callbacks' => array(
                        'label' => "function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': $' + context.parsed.toLocaleString() + ' (' + percentage + '%)';
                        }",
                    ),
                ),
            ),
        ),
    );
}

/**
 * Generate market heatmap data
 */
function stock_scanner_generate_heatmap_data($stocks_data) {
    $heatmap_data = array();
    
    if (!empty($stocks_data) && is_array($stocks_data)) {
        foreach ($stocks_data as $stock) {
            if (isset($stock['ticker']) && isset($stock['price_change_percent']) && isset($stock['market_cap'])) {
                $change_percent = floatval($stock['price_change_percent']);
                $market_cap = floatval($stock['market_cap']);
                
                $heatmap_data[] = array(
                    'ticker' => strtoupper($stock['ticker']),
                    'company_name' => isset($stock['company_name']) ? $stock['company_name'] : $stock['ticker'],
                    'change_percent' => $change_percent,
                    'market_cap' => $market_cap,
                    'size' => stock_scanner_calculate_heatmap_size($market_cap),
                    'color' => stock_scanner_get_heatmap_color($change_percent),
                    'formatted_change' => stock_scanner_format_percentage($change_percent),
                    'formatted_market_cap' => stock_scanner_format_market_cap($market_cap),
                );
            }
        }
    }
    
    // Sort by market cap for better visual hierarchy
    usort($heatmap_data, function($a, $b) {
        return $b['market_cap'] - $a['market_cap'];
    });
    
    return $heatmap_data;
}

/**
 * Calculate heatmap cell size based on market cap
 */
function stock_scanner_calculate_heatmap_size($market_cap) {
    if ($market_cap >= 200000000000) {
        return 'xl'; // Mega cap
    } elseif ($market_cap >= 10000000000) {
        return 'lg'; // Large cap
    } elseif ($market_cap >= 2000000000) {
        return 'md'; // Mid cap
    } elseif ($market_cap >= 300000000) {
        return 'sm'; // Small cap
    } else {
        return 'xs'; // Micro/Nano cap
    }
}

/**
 * Get heatmap color based on price change
 */
function stock_scanner_get_heatmap_color($change_percent) {
    $change = floatval($change_percent);
    
    if ($change >= 5) {
        return 'bg-green-600 text-white';
    } elseif ($change >= 2) {
        return 'bg-green-400 text-white';
    } elseif ($change >= 0.5) {
        return 'bg-green-200 text-green-900';
    } elseif ($change > -0.5) {
        return 'bg-gray-100 text-gray-900';
    } elseif ($change > -2) {
        return 'bg-red-200 text-red-900';
    } elseif ($change > -5) {
        return 'bg-red-400 text-white';
    } else {
        return 'bg-red-600 text-white';
    }
}

/**
 * Generate color palette for charts
 */
function stock_scanner_generate_color_palette($count) {
    $base_colors = array(
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1',
        '#14b8a6', '#eab308', '#dc2626', '#7c3aed', '#0ea5e9',
    );
    
    $backgrounds = array();
    $borders = array();
    
    for ($i = 0; $i < $count; $i++) {
        $color = $base_colors[$i % count($base_colors)];
        $backgrounds[] = $color . '20'; // 20% opacity
        $borders[] = $color;
    }
    
    return array(
        'backgrounds' => $backgrounds,
        'borders' => $borders,
        'base_colors' => array_slice($base_colors, 0, $count),
    );
}

/**
 * Generate candlestick chart data
 */
function stock_scanner_generate_candlestick_data($ohlc_data) {
    $candlestick_data = array();
    
    if (!empty($ohlc_data) && is_array($ohlc_data)) {
        foreach ($ohlc_data as $data_point) {
            $candlestick_data[] = array(
                'x' => $data_point['timestamp'],
                'o' => floatval($data_point['open']),
                'h' => floatval($data_point['high']),
                'l' => floatval($data_point['low']),
                'c' => floatval($data_point['close']),
            );
        }
    }
    
    return array(
        'type' => 'candlestick',
        'data' => array(
            'datasets' => array(
                array(
                    'label' => 'Price',
                    'data' => $candlestick_data,
                    'borderColor' => array(
                        'up' => '#10b981',
                        'down' => '#ef4444',
                        'unchanged' => '#6b7280',
                    ),
                    'backgroundColor' => array(
                        'up' => 'rgba(16, 185, 129, 0.1)',
                        'down' => 'rgba(239, 68, 68, 0.1)',
                        'unchanged' => 'rgba(107, 114, 128, 0.1)',
                    ),
                ),
            ),
        ),
        'options' => array(
            'responsive' => true,
            'maintainAspectRatio' => false,
            'scales' => array(
                'x' => array(
                    'type' => 'time',
                    'time' => array(
                        'unit' => 'day',
                    ),
                ),
                'y' => array(
                    'beginAtZero' => false,
                ),
            ),
        ),
    );
}

/**
 * Generate technical indicators data
 */
function stock_scanner_generate_technical_indicators($price_data, $indicators = array('sma', 'ema', 'rsi')) {
    $result = array();
    
    if (in_array('sma', $indicators)) {
        $result['sma'] = stock_scanner_calculate_sma($price_data, 20);
    }
    
    if (in_array('ema', $indicators)) {
        $result['ema'] = stock_scanner_calculate_ema($price_data, 20);
    }
    
    if (in_array('rsi', $indicators)) {
        $result['rsi'] = stock_scanner_calculate_rsi($price_data, 14);
    }
    
    if (in_array('macd', $indicators)) {
        $result['macd'] = stock_scanner_calculate_macd($price_data);
    }
    
    return $result;
}

/**
 * Calculate Simple Moving Average
 */
function stock_scanner_calculate_sma($prices, $period = 20) {
    $sma = array();
    $price_values = array_column($prices, 'close');
    
    for ($i = $period - 1; $i < count($price_values); $i++) {
        $sum = 0;
        for ($j = 0; $j < $period; $j++) {
            $sum += $price_values[$i - $j];
        }
        $sma[] = round($sum / $period, 2);
    }
    
    return $sma;
}

/**
 * Calculate Exponential Moving Average
 */
function stock_scanner_calculate_ema($prices, $period = 20) {
    $ema = array();
    $price_values = array_column($prices, 'close');
    $k = 2 / ($period + 1);
    
    // Start with SMA for first value
    $sum = 0;
    for ($i = 0; $i < $period; $i++) {
        $sum += $price_values[$i];
    }
    $ema[0] = $sum / $period;
    
    // Calculate EMA for remaining values
    for ($i = 1; $i < count($price_values) - $period + 1; $i++) {
        $ema[$i] = round($price_values[$i + $period - 1] * $k + $ema[$i - 1] * (1 - $k), 2);
    }
    
    return $ema;
}

/**
 * Calculate Relative Strength Index
 */
function stock_scanner_calculate_rsi($prices, $period = 14) {
    $rsi = array();
    $price_values = array_column($prices, 'close');
    
    $gains = array();
    $losses = array();
    
    // Calculate gains and losses
    for ($i = 1; $i < count($price_values); $i++) {
        $change = $price_values[$i] - $price_values[$i - 1];
        $gains[] = $change > 0 ? $change : 0;
        $losses[] = $change < 0 ? abs($change) : 0;
    }
    
    // Calculate RSI
    for ($i = $period - 1; $i < count($gains); $i++) {
        $avg_gain = array_sum(array_slice($gains, $i - $period + 1, $period)) / $period;
        $avg_loss = array_sum(array_slice($losses, $i - $period + 1, $period)) / $period;
        
        if ($avg_loss == 0) {
            $rsi[] = 100;
        } else {
            $rs = $avg_gain / $avg_loss;
            $rsi[] = round(100 - (100 / (1 + $rs)), 2);
        }
    }
    
    return $rsi;
}

/**
 * Calculate MACD
 */
function stock_scanner_calculate_macd($prices) {
    $price_values = array_column($prices, 'close');
    
    $ema_12 = stock_scanner_calculate_ema($prices, 12);
    $ema_26 = stock_scanner_calculate_ema($prices, 26);
    
    $macd_line = array();
    $min_length = min(count($ema_12), count($ema_26));
    
    for ($i = 0; $i < $min_length; $i++) {
        $macd_line[] = round($ema_12[$i] - $ema_26[$i], 4);
    }
    
    // Calculate signal line (9-period EMA of MACD line)
    $signal_line = stock_scanner_calculate_ema(
        array_map(function($value) { return array('close' => $value); }, $macd_line),
        9
    );
    
    // Calculate histogram
    $histogram = array();
    $min_signal_length = min(count($macd_line), count($signal_line));
    
    for ($i = 0; $i < $min_signal_length; $i++) {
        $histogram[] = round($macd_line[$i] - $signal_line[$i], 4);
    }
    
    return array(
        'macd' => $macd_line,
        'signal' => $signal_line,
        'histogram' => $histogram,
    );
}

/**
 * Generate chart HTML container
 */
function stock_scanner_render_chart_container($id, $options = array()) {
    $default_options = array(
        'height' => 400,
        'class' => '',
        'title' => '',
    );
    
    $options = wp_parse_args($options, $default_options);
    
    $html = '<div class="chart-container ' . esc_attr($options['class']) . '">';
    
    if (!empty($options['title'])) {
        $html .= '<h3 class="chart-title text-lg font-semibold mb-4">' . esc_html($options['title']) . '</h3>';
    }
    
    $html .= '<div class="chart-wrapper" style="position: relative; height: ' . intval($options['height']) . 'px;">';
    $html .= '<canvas id="' . esc_attr($id) . '"></canvas>';
    $html .= '</div>';
    $html .= '</div>';
    
    return $html;
}