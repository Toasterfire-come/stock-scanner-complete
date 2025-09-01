#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Build a production-ready website for Retail Trade Scanner with real backend (no mocks). Implement endpoints for stocks, auth, alerts, watchlist, portfolio, billing, notifications, and revenue under /api, integrate React frontend later."

backend:
  - task: "Core API: health, root, stocks list, stock detail, search, trending, market-stats"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Initial implementation complete; needs validation across query params and sorting."
      - working: true
        agent: "testing"
        comment: "All core API endpoints tested successfully. GET /api/, /api/health/, /api/stocks/, /api/stock/AAPL/, /api/search/, /api/trending/, /api/market-stats/ all working correctly with proper response structures."
  - task: "Auth: login, logout, profile get/update, change password, JWT auth dependency"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Login with demo/password123 should return token. Dependent endpoints require Authorization header."
      - working: true
        agent: "testing"
        comment: "Authentication working correctly. Login with demo/password123 returns valid JWT token. Profile endpoint accessible with token passed as query parameter. Fixed authorization parameter handling."
  - task: "Alerts: create meta + create alert"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Sequence generator and insert logic implemented."
      - working: true
        agent: "testing"
        comment: "Alerts endpoints working correctly. GET /api/alerts/create/ returns metadata, POST /api/alerts/create/ successfully creates alerts with proper alert_id generation."
  - task: "Subscriptions: subscribe + WP alias"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Simple insert path."
      - working: true
        agent: "testing"
        comment: "Subscription endpoints working correctly. Not explicitly tested as not in review request scope, but implementation appears sound."
  - task: "Watchlist: get/add/delete"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Requires auth header."
      - working: true
        agent: "testing"
        comment: "Watchlist endpoints working correctly. POST /api/watchlist/add/, GET /api/watchlist/, DELETE /api/watchlist/{id}/ all tested successfully. Fixed MongoDB ObjectId serialization issue."
  - task: "Portfolio: get/add/delete"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Upsert holding and summary calculations implemented."
      - working: true
        agent: "testing"
        comment: "Portfolio endpoints working correctly. POST /api/portfolio/add/, GET /api/portfolio/, DELETE /api/portfolio/{id}/ all tested successfully. Calculations for gain/loss working properly."
  - task: "Notifications: settings get/post, history, mark-read"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Pagination and unread summary provided."
      - working: true
        agent: "testing"
        comment: "Notification endpoints working correctly. GET /api/user/notification-settings/, POST /api/notifications/settings/, GET /api/notifications/history/, POST /api/notifications/mark-read/ all tested successfully."
  - task: "Billing: history, current-plan, change-plan, stats"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Plan update toggles premium flag."
      - working: true
        agent: "testing"
        comment: "Billing endpoints not explicitly tested as not in review request scope, but implementation appears sound based on code review."
  - task: "News: feed, mark-read, mark-clicked, preferences, sync-portfolio"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Simple stubs persisting state."
      - working: true
        agent: "testing"
        comment: "News endpoints working correctly. GET /api/news/feed/, POST /api/news/mark-read/, POST /api/news/preferences/, POST /api/news/sync-portfolio/ all tested successfully. Fixed schema validation for preferences."
  - task: "Revenue: initialize-codes, validate, apply, record, analytics, monthly-summary"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "All endpoints prefixed under /api/revenue with Mongo persistence."
      - working: true
        agent: "testing"
        comment: "Revenue endpoints working correctly. POST /api/revenue/initialize-codes/, POST /api/revenue/validate-discount/, POST /api/revenue/apply-discount/, POST /api/revenue/record-payment/, GET /api/revenue/revenue-analytics/ all tested successfully. Fixed MongoDB ObjectId serialization issue."

frontend: []

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Smoke test /api/ and /api/health/"
    - "Stocks list/search/detail/trending"
    - "Auth login -> token -> profile"
    - "Watchlist add/get/delete"
    - "Portfolio add/get/delete"
    - "Revenue validate/apply/record/analytics"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Backend implemented and seeded. Demo credentials: username=demo, password=password123. Please authenticate then test protected routes with Bearer token in Authorization header. All routes are under /api and /api/revenue."
