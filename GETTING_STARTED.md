# Getting Started: Orange.ro API Discovery

## Step 1: Set Up Interceptor

1. **Copy interceptor from hidroelectrica project:**
   ```bash
   cd /Users/mac-ria-ebesliu/agents/homeassistant/orange
   cp ../hidroelectrica/interceptor.py .
   cp ../hidroelectrica/start_interceptor.sh .
   ```

2. **Create captured_requests directory:**
   ```bash
   mkdir -p captured_requests
   ```

3. **Install dependencies:**
   ```bash
   pip install mitmproxy aiohttp
   ```

## Step 2: Capture Orange.ro Traffic

1. **Start the interceptor:**
   ```bash
   ./start_interceptor.sh
   # Or manually:
   mitmdump -s interceptor.py --set block_global=false
   ```

2. **Configure browser proxy:**
   - Host: `localhost`
   - Port: `8080`
   - Enable for HTTP and HTTPS

3. **Install mitmproxy certificate:**
   - Visit: `http://mitm.it`
   - Download and install certificate for your browser

4. **Navigate Orange.ro:**
   - Login to orange.ro
   - View account dashboard
   - Check subscriptions page
   - View bills/invoices page
   - Check usage/consumption page

5. **Stop interceptor** (Ctrl+C)

## Step 3: Analyze Captured Requests

1. **Review captured files:**
   ```bash
   ls -la captured_requests/
   ```

2. **Look for key endpoints:**
   - Login/authentication endpoints
   - Account balance/info endpoints
   - Subscriptions list endpoints
   - Bills/invoices endpoints
   - Usage/consumption endpoints

3. **Analyze request/response structure:**
   - HTTP method (GET/POST)
   - Headers (cookies, CSRF tokens)
   - Request body format
   - Response JSON structure

## Step 4: Update Integration Code

Based on discovered endpoints, update:

1. **`const.py`** - Add real API endpoints
2. **`api.py`** - Implement authentication and data fetching
3. **Test authentication** in isolation before adding sensors

## Expected Orange.ro Data

### Account Information
- Balance/credit
- Account holder name
- Customer ID
- Payment method

### Subscriptions
- Mobile subscriptions (phone numbers)
- Internet subscriptions
- TV subscriptions
- Status (active/suspended)
- Plan name and details

### Bills
- Unpaid bills count
- Total amount due
- Individual bill details
- Due dates

### Usage (if available)
- Mobile data used/remaining
- Voice minutes used/remaining
- SMS count

## Tips

1. **Check Network Tab** in browser DevTools alongside interceptor
2. **Look for XHR/Fetch requests** to API endpoints
3. **Note authentication tokens** - may expire quickly
4. **Test API calls** with curl/Postman before coding
5. **Document everything** - API may change

## Next Steps

After API discovery:
1. Implement authentication in `api.py`
2. Implement data fetching methods
3. Create sensor entities in `sensor.py`
4. Add config flow for UI setup
5. Test integration in Home Assistant

---

See [AGENTS.md](AGENTS.md) for detailed coding guidelines.
