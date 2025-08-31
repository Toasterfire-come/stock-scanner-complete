<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?php _e('Website Temporarily Unavailable', 'retail-trade-scanner'); ?></title>
    <style>
        :root {
            --drab-dark-brown: #433e0e;
            --yinmn-blue: #374a67;
            --indian-red: #e15554;
            --silver: #c1bdb3;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--drab-dark-brown);
            color: var(--silver);
            margin: 0;
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .error-container {
            text-align: center;
            max-width: 600px;
            padding: 40px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            border: 1px solid rgba(193, 189, 179, 0.2);
        }
        
        .error-code {
            font-size: 4rem;
            font-weight: bold;
            color: var(--indian-red);
            margin: 0 0 20px 0;
        }
        
        .error-title {
            font-size: 1.5rem;
            margin: 0 0 20px 0;
            color: var(--silver);
        }
        
        .error-message {
            color: rgba(193, 189, 179, 0.8);
            line-height: 1.6;
            margin: 0 0 30px 0;
        }
        
        .error-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: var(--yinmn-blue);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .btn:hover {
            background: #4a5c7a;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: transparent;
            border: 1px solid var(--silver);
            color: var(--silver);
        }
        
        .btn-secondary:hover {
            background: var(--silver);
            color: var(--drab-dark-brown);
        }
        
        @media (max-width: 480px) {
            .error-container {
                padding: 20px;
            }
            
            .error-code {
                font-size: 3rem;
            }
            
            .error-actions {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">500</div>
        <h1 class="error-title"><?php _e('Website Temporarily Unavailable', 'retail-trade-scanner'); ?></h1>
        <p class="error-message">
            <?php _e('We apologize for the inconvenience. Our website is experiencing technical difficulties and our team has been notified. Please try again in a few minutes.', 'retail-trade-scanner'); ?>
        </p>
        <div class="error-actions">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="btn">
                <?php _e('Go to Homepage', 'retail-trade-scanner'); ?>
            </a>
            <a href="javascript:history.back()" class="btn btn-secondary">
                <?php _e('Go Back', 'retail-trade-scanner'); ?>
            </a>
        </div>
    </div>
    
    <script>
        // Auto-retry after 5 seconds
        setTimeout(function() {
            const retryBtn = document.createElement('button');
            retryBtn.className = 'btn';
            retryBtn.textContent = '<?php _e('Retry Now', 'retail-trade-scanner'); ?>';
            retryBtn.onclick = function() { location.reload(); };
            document.querySelector('.error-actions').appendChild(retryBtn);
        }, 5000);
    </script>
</body>
</html>