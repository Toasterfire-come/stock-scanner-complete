#!/bin/bash

# Proxy Manager Runner Script
# Provides various options for running the proxy scraper and validator

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
THREADS=50
TIMEOUT=10
INTERVAL=30
OUTPUT="working_proxies.json"

# Function to display help
show_help() {
    echo "Proxy Manager Runner Script"
    echo "============================"
    echo ""
    echo "Usage: $0 [OPTION]..."
    echo ""
    echo "Options:"
    echo "  scrape        - Run single scrape and validation cycle"
    echo "  schedule      - Run in scheduler mode (every 30 minutes)"
    echo "  maintenance   - Run maintenance check on existing proxies"
    echo "  stats         - Show proxy statistics"
    echo "  test          - Test proxy scraping without validation"
    echo "  validate      - Validate existing scraped proxies"
    echo "  integrate     - Run integrated manager with stock scraper support"
    echo "  help          - Show this help message"
    echo ""
    echo "Advanced Options:"
    echo "  --threads N   - Number of validation threads (default: 50)"
    echo "  --timeout N   - Request timeout in seconds (default: 10)"
    echo "  --interval N  - Schedule interval in minutes (default: 30)"
    echo "  --output FILE - Output file name (default: working_proxies.json)"
    echo "  --github      - Include GitHub repository scraping"
    echo ""
    echo "Examples:"
    echo "  $0 scrape                    # Run single scrape and validation"
    echo "  $0 schedule --interval 60    # Run every 60 minutes"
    echo "  $0 maintenance               # Check health of existing proxies"
    echo "  $0 integrate schedule        # Run integrated manager in schedule mode"
}

# Function to check Python and install requirements
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed!${NC}"
        exit 1
    fi
    
    # Check if requirements are installed
    if ! python3 -c "import requests" 2>/dev/null; then
        echo -e "${YELLOW}Installing required packages...${NC}"
        pip3 install -r requirements_proxy.txt
    fi
    
    echo -e "${GREEN}Requirements satisfied${NC}"
}

# Function to run proxy scraper
run_scraper() {
    local mode=$1
    shift
    
    case $mode in
        "scrape")
            echo -e "${GREEN}Running single scrape and validation cycle...${NC}"
            python3 proxy_scraper_validator.py \
                -threads $THREADS \
                -timeout $TIMEOUT \
                -output "$OUTPUT" \
                $@
            ;;
        
        "schedule")
            echo -e "${GREEN}Running in scheduler mode (every $INTERVAL minutes)...${NC}"
            python3 proxy_scraper_validator.py \
                -schedule \
                -threads $THREADS \
                -timeout $TIMEOUT \
                -output "$OUTPUT" \
                $@
            ;;
        
        "test")
            echo -e "${GREEN}Running scrape-only mode (no validation)...${NC}"
            python3 proxy_scraper_validator.py \
                -scrape-only \
                -output "$OUTPUT" \
                $@
            ;;
        
        "validate")
            echo -e "${GREEN}Validating existing proxies...${NC}"
            if [ -f "all_scraped_proxies.json" ]; then
                python3 proxy_scraper_validator.py \
                    -validate-only all_scraped_proxies.json \
                    -threads $THREADS \
                    -timeout $TIMEOUT \
                    -output "$OUTPUT" \
                    $@
            else
                echo -e "${RED}No scraped proxies found. Run 'scrape' first.${NC}"
                exit 1
            fi
            ;;
        
        *)
            echo -e "${RED}Unknown scraper mode: $mode${NC}"
            exit 1
            ;;
    esac
}

# Function to run integrated manager
run_integrated() {
    local mode=$1
    shift
    
    case $mode in
        "schedule")
            echo -e "${GREEN}Running integrated manager in scheduler mode...${NC}"
            python3 integrated_proxy_manager.py \
                -schedule \
                -interval $INTERVAL \
                -threads $THREADS \
                -timeout $TIMEOUT \
                -output "$OUTPUT" \
                $@
            ;;
        
        "maintenance")
            echo -e "${GREEN}Running maintenance mode...${NC}"
            python3 integrated_proxy_manager.py \
                -maintenance \
                -threads $THREADS \
                -timeout $TIMEOUT \
                -output "$OUTPUT" \
                $@
            ;;
        
        "stats")
            echo -e "${GREEN}Showing proxy statistics...${NC}"
            python3 integrated_proxy_manager.py -stats
            ;;
        
        *)
            echo -e "${GREEN}Running integrated manager (single cycle)...${NC}"
            python3 integrated_proxy_manager.py \
                -threads $THREADS \
                -timeout $TIMEOUT \
                -output "$OUTPUT" \
                $@
            ;;
    esac
}

# Parse command line arguments
COMMAND=""
EXTRA_ARGS=""
GITHUB_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        scrape|schedule|maintenance|stats|test|validate|integrate|help)
            COMMAND=$1
            shift
            ;;
        --threads)
            THREADS=$2
            shift 2
            ;;
        --timeout)
            TIMEOUT=$2
            shift 2
            ;;
        --interval)
            INTERVAL=$2
            shift 2
            ;;
        --output)
            OUTPUT=$2
            shift 2
            ;;
        --github)
            GITHUB_FLAG="-github-repos"
            shift
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Execute based on command
case $COMMAND in
    help|"")
        show_help
        ;;
    
    scrape|test|validate)
        check_requirements
        run_scraper $COMMAND $GITHUB_FLAG $EXTRA_ARGS
        ;;
    
    schedule)
        check_requirements
        run_scraper schedule $GITHUB_FLAG $EXTRA_ARGS
        ;;
    
    maintenance|stats)
        check_requirements
        run_integrated $COMMAND $GITHUB_FLAG $EXTRA_ARGS
        ;;
    
    integrate)
        check_requirements
        # Check if there's a subcommand
        if [[ -n "$EXTRA_ARGS" ]]; then
            run_integrated $EXTRA_ARGS $GITHUB_FLAG
        else
            run_integrated "single" $GITHUB_FLAG
        fi
        ;;
    
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac

# Check exit status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Operation completed successfully${NC}"
else
    echo -e "${RED}Operation failed${NC}"
    exit 1
fi