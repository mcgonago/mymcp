# Analysis: Horizon/Glance Direct Mode Upload Implementation

## Original Inquiry

**Date:** October 28, 2025  
**Asked to:** @github-reviewer-agent  
**Query:**
```
please search for any work done with respect to Horizon/Glance and the changes made 
(CORS, httpd.conf, ..) to support direct mode upload by default
```

## Data Sources

- [x] GitHub PRs (openstack-k8s-operators repositories)
- [ ] OpenDev Reviews (openstack/horizon, openstack/glance)
- [ ] GitLab MRs
- [ ] Jira Issues
- [ ] Other: Operator configurations

**[To be populated with specific sources from github-reviewer-agent]**

## Executive Summary

Direct mode upload is a performance optimization for OpenStack Horizon that allows image uploads to flow directly from the user's browser to the Glance API, rather than proxying through Horizon. This reduces load on Horizon servers and improves upload speeds for large images.

**Key Technical Requirements:**
- CORS (Cross-Origin Resource Sharing) configuration in Glance to allow browser-initiated requests from Horizon's domain
- Apache httpd.conf modifications in Horizon to properly handle CORS headers
- Configuration changes to enable direct mode in Horizon settings

**Status:** Awaiting detailed findings from github-reviewer-agent regarding specific PRs, commits, and implementation details in the openstack-k8s-operators repositories.

## Background

### Traditional Proxy Mode Architecture

In the traditional proxy mode, image uploads follow this path:
```
User Browser → Horizon (Django/WSGI) → Glance API → Storage Backend
```

**Limitations:**
1. **Resource Intensive:** Horizon acts as a proxy, consuming memory and CPU for data transfer
2. **Bandwidth Bottleneck:** Data is transferred twice (browser→Horizon, Horizon→Glance)
3. **Scalability Issues:** Large uploads can overwhelm Horizon processes
4. **Timeout Problems:** Long uploads may hit Django/WSGI timeout limits
5. **Memory Pressure:** Large files buffered in Horizon's memory

### Direct Mode Architecture

Direct mode changes the upload path to:
```
User Browser → Glance API (direct CORS request) → Storage Backend
                ↑
                └─ Horizon provides auth token and coordinates
```

**Benefits:**
1. **Reduced Load:** Horizon only coordinates, doesn't proxy data
2. **Better Performance:** Single data transfer, no double bandwidth usage
3. **Improved Scalability:** Glance handles uploads directly
4. **Faster Uploads:** No intermediary buffering delays
5. **Resource Efficiency:** Horizon freed for other operations

### Why CORS is Required

When a browser makes a cross-origin request (from Horizon's domain to Glance's domain), the browser's Same-Origin Policy requires CORS headers. Without proper CORS configuration:
- Browser blocks the request
- Upload fails with CORS error in console
- User sees generic error message

**CORS Requirements:**
- Glance must return `Access-Control-Allow-Origin` header matching Horizon's origin
- Glance must handle OPTIONS preflight requests
- Credentials (auth tokens) must be explicitly allowed
- Specific headers (X-Auth-Token, etc.) must be whitelisted

## Detailed Findings

### Architecture Changes

**[To be populated with specific implementation details from github-reviewer-agent]**

Expected changes:
1. Horizon configuration to enable direct mode
2. Glance CORS middleware configuration
3. Apache/httpd proxy configuration updates
4. Operator templates for Kubernetes deployments

### CORS Implementation Requirements

#### Browser Security Model

Modern browsers enforce the Same-Origin Policy (SOP):
```
Origin: protocol + domain + port
Example: https://horizon.example.com:443
```

Any request from `https://horizon.example.com` to `https://glance.example.com` is cross-origin and requires CORS approval.

#### CORS Flow

1. **Preflight Request (OPTIONS):**
   ```http
   OPTIONS /v2/images HTTP/1.1
   Origin: https://horizon.example.com
   Access-Control-Request-Method: POST
   Access-Control-Request-Headers: X-Auth-Token
   ```

2. **Glance Response:**
   ```http
   HTTP/1.1 200 OK
   Access-Control-Allow-Origin: https://horizon.example.com
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE
   Access-Control-Allow-Headers: X-Auth-Token, Content-Type
   Access-Control-Allow-Credentials: true
   Access-Control-Max-Age: 3600
   ```

3. **Actual Upload Request:**
   ```http
   POST /v2/images HTTP/1.1
   Origin: https://horizon.example.com
   X-Auth-Token: <token>
   Content-Type: application/octet-stream
   [image data]
   ```

### Configuration Components

#### Glance CORS Configuration

**[To be populated with actual configuration from PRs]**

Expected configuration in `glance-api.conf`:
```ini
[cors]
# Allow requests from Horizon
allowed_origin = https://horizon.example.com,https://horizon.alt.example.com

# Allow credentials (auth tokens)
allow_credentials = true

# Headers that can be sent to Glance
allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token,X-OpenStack-Request-ID

# Headers that Glance can expose to browser
expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token,X-OpenStack-Request-ID

# How long browser can cache preflight response
max_age = 3600
```

#### Horizon Configuration

**[To be populated with actual configuration from PRs]**

Expected configuration in `local_settings.py`:
```python
# Enable direct upload mode
OPENSTACK_GLANCE_DIRECT_UPLOAD = True

# Glance endpoint for direct uploads
GLANCE_ENDPOINT = 'https://glance.example.com:9292'

# CORS origins (if Horizon needs to set headers)
CORS_ALLOWED_ORIGINS = ['https://glance.example.com']
```

#### Apache httpd.conf Changes

**[To be populated with actual configuration from PRs]**

Expected changes in Horizon's Apache configuration:
```apache
<VirtualHost *:443>
    ServerName horizon.example.com
    
    # CORS headers for Glance communication
    Header always set Access-Control-Allow-Origin "https://glance.example.com"
    Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
    Header always set Access-Control-Allow-Headers "Content-Type, X-Auth-Token, X-Subject-Token"
    Header always set Access-Control-Allow-Credentials "true"
    
    # Handle OPTIONS preflight requests
    <Location />
        <If "%{REQUEST_METHOD} == 'OPTIONS'">
            Header set Access-Control-Max-Age "3600"
        </If>
    </Location>
    
    # Existing proxy configuration
    ProxyPass /api/glance http://glance-api:9292/
    ProxyPassReverse /api/glance http://glance-api:9292/
    
    # Rest of Horizon configuration...
</VirtualHost>
```

## Code References

### GitHub Pull Requests

**[To be populated with PRs from github-reviewer-agent]**

Expected repositories to check:
- `openstack-k8s-operators/horizon-operator`
- `openstack-k8s-operators/glance-operator`
- `openstack-k8s-operators/openstack-operator`

### OpenDev Reviews

**[To be populated]**

Search terms for opendev.org:
- "direct upload" in openstack/horizon
- "CORS" in openstack/glance
- "direct mode" configuration changes

### Commit References

**[To be populated with specific commits]**

Expected files modified:
- Horizon operator templates
- Glance operator configuration
- httpd.conf templates
- Custom resource definitions (CRDs)

### File Paths

**[To be populated with specific paths from PRs]**

Expected files:
- `config/samples/horizon_*.yaml` - Sample configurations
- `templates/horizon/httpd.conf` - Apache configuration template
- `controllers/horizon_controller.go` - Reconciliation logic
- `config/samples/glance_*.yaml` - Glance CORS config

## Implementation Timeline

**[To be populated with dates from commits/PRs]**

| Date | Event | Link |
|------|-------|------|
| TBD | Initial direct mode PR | [To be populated] |
| TBD | CORS configuration added | [To be populated] |
| TBD | httpd.conf template updated | [To be populated] |
| TBD | Documentation updated | [To be populated] |
| TBD | Merged to main | [To be populated] |

## Testing and Verification

### Test Cases

#### Test Case 1: Verify CORS Headers

```bash
# Test CORS preflight from command line
curl -I -X OPTIONS \
  -H "Origin: https://horizon.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Auth-Token" \
  https://glance.example.com:9292/v2/images

# Expected response headers:
# HTTP/1.1 200 OK
# Access-Control-Allow-Origin: https://horizon.example.com
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
# Access-Control-Allow-Headers: X-Auth-Token, Content-Type
# Access-Control-Allow-Credentials: true
# Access-Control-Max-Age: 3600
```

**Expected result:** CORS headers present with correct origin and methods

#### Test Case 2: Upload Image via Horizon UI

```bash
# 1. Open Horizon in browser
# 2. Navigate to Project → Compute → Images
# 3. Click "Create Image"
# 4. Select "File" as source
# 5. Choose a test image file
# 6. Open browser Developer Tools → Network tab
# 7. Click "Create Image"

# Expected behavior:
# - OPTIONS request to glance.example.com (preflight)
# - POST request to glance.example.com (upload)
# - No proxy through horizon.example.com/api/glance
# - Upload progress visible
# - No CORS errors in console
```

**Expected result:** Upload succeeds without CORS errors, traffic goes directly to Glance

#### Test Case 3: Verify Horizon Resource Usage

```bash
# Monitor Horizon pod during direct mode upload
kubectl top pod -n openstack | grep horizon

# During upload:
# - CPU should remain low (no data proxying)
# - Memory should remain stable (no buffering)

# Compare with proxy mode:
# - Proxy mode: High CPU/memory during upload
# - Direct mode: Minimal resource usage
```

**Expected result:** Horizon resource usage remains low during direct mode uploads

### Verification Commands

```bash
# Check Glance CORS configuration
openstack-config --get /etc/glance/glance-api.conf cors allowed_origin
openstack-config --get /etc/glance/glance-api.conf cors allow_credentials

# Check Horizon configuration (in pod)
kubectl exec -n openstack horizon-xxxx -- \
  python3 -c "from django.conf import settings; print(settings.OPENSTACK_GLANCE_DIRECT_UPLOAD)"

# Check Apache configuration
kubectl exec -n openstack horizon-xxxx -- cat /etc/httpd/conf.d/horizon.conf | grep -A 5 "CORS"

# Test CORS from external client
curl -i -X OPTIONS \
  -H "Origin: $(oc get route horizon -n openstack -o jsonpath='{.spec.host}')" \
  -H "Access-Control-Request-Method: POST" \
  "$(oc get route glance -n openstack -o jsonpath='{.spec.host}')/v2/images"
```

## Configuration Examples

### Full Glance CORS Configuration

```ini
# /etc/glance/glance-api.conf

[DEFAULT]
# ... other settings ...

[cors]
# Multiple origins can be specified
allowed_origin = https://horizon.example.com,https://horizon.alt.example.com

# Required for auth token support
allow_credentials = true

# Headers that can be sent in requests
allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token,X-OpenStack-Request-ID,Content-Disposition

# Headers that can be exposed to JavaScript
expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token,X-OpenStack-Request-ID,Content-Disposition,Location

# Methods allowed
allow_methods = GET,POST,PUT,DELETE,OPTIONS,PATCH

# Cache preflight responses for 1 hour
max_age = 3600
```

### Full Horizon Configuration

```python
# /etc/openstack-dashboard/local_settings.d/direct_upload.py

# Enable direct upload to Glance
OPENSTACK_GLANCE_DIRECT_UPLOAD = True

# Glance public endpoint (must be accessible from user's browser)
GLANCE_ENDPOINT = 'https://glance.example.com:9292'

# CORS configuration (if needed on Horizon side)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://glance.example.com',
]

# Preflight caching
CORS_PREFLIGHT_MAX_AGE = 3600
```

### Apache Configuration (Full)

```apache
<VirtualHost *:443>
    ServerName horizon.example.com
    DocumentRoot /var/www/html
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/horizon.crt
    SSLCertificateKeyFile /etc/pki/tls/private/horizon.key
    
    # CORS Headers for Direct Upload
    # These allow Horizon's JavaScript to communicate with Glance
    Header always set Access-Control-Allow-Origin "https://glance.example.com"
    Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    Header always set Access-Control-Allow-Headers "Content-Type, X-Auth-Token, X-Subject-Token, X-OpenStack-Request-ID"
    Header always set Access-Control-Expose-Headers "X-Auth-Token, X-Subject-Token, X-OpenStack-Request-ID"
    Header always set Access-Control-Allow-Credentials "true"
    
    # Handle OPTIONS preflight requests efficiently
    <Location />
        <If "%{REQUEST_METHOD} == 'OPTIONS'">
            Header set Access-Control-Max-Age "3600"
            Header set Content-Type "text/plain"
        </If>
    </Location>
    
    # Django/WSGI Configuration
    WSGIDaemonProcess horizon user=apache group=apache processes=4 threads=25 display-name=%{GROUP}
    WSGIProcessGroup horizon
    WSGIScriptAlias / /usr/share/openstack-dashboard/openstack_dashboard/wsgi.py
    WSGIPassAuthorization On
    
    # Static files
    Alias /static /usr/share/openstack-dashboard/static
    <Directory /usr/share/openstack-dashboard/static>
        Require all granted
    </Directory>
    
    <Directory /usr/share/openstack-dashboard/openstack_dashboard>
        Require all granted
    </Directory>
    
    # Logging
    ErrorLog /var/log/httpd/horizon_error.log
    CustomLog /var/log/httpd/horizon_access.log combined
</VirtualHost>
```

### Kubernetes Operator CRD Example

```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  # ... other spec fields ...
  
  # Direct upload configuration
  directUpload:
    enabled: true
    glanceEndpoint: "https://glance.openstack.svc.cluster.local:9292"
  
  # CORS configuration
  cors:
    enabled: true
    allowedOrigins:
      - "https://glance.openstack.svc.cluster.local"
    allowCredentials: true
    maxAge: 3600
```

## Known Issues and Workarounds

### Issue 1: Browser Blocks Mixed Content

**Problem:** If Horizon uses HTTPS but Glance uses HTTP, browsers block the request as "mixed content".

**Error in Console:**
```
Mixed Content: The page at 'https://horizon.example.com' was loaded over HTTPS, 
but requested an insecure resource 'http://glance.example.com'. This request has been blocked.
```

**Workaround:**
```yaml
# Ensure Glance also uses HTTPS
apiVersion: glance.openstack.org/v1beta1
kind: Glance
spec:
  tls:
    enabled: true
    secretName: glance-tls-secret
```

### Issue 2: CORS Preflight Timeout

**Problem:** Glance takes too long to respond to OPTIONS requests, causing browser timeout.

**Symptoms:**
- Upload hangs
- Browser shows "net::ERR_CONNECTION_TIMED_OUT"
- Network tab shows OPTIONS request pending

**Workaround:**
```ini
# In glance-api.conf, ensure CORS middleware is early in pipeline
[paste_deploy]
flavor = keystone+cors

# Make sure cors is before other middleware
```

### Issue 3: Wildcard Origin Not Working

**Problem:** Using `allowed_origin = *` doesn't work with `allow_credentials = true`.

**Error:**
```
The CORS protocol does not allow specifying a wildcard (any) origin and credentials at the same time.
```

**Workaround:**
```ini
# Explicitly list all Horizon origins instead of wildcard
allowed_origin = https://horizon1.example.com,https://horizon2.example.com
allow_credentials = true
```

### Issue 4: Large File Upload Fails

**Problem:** Very large files (>5GB) timeout even in direct mode.

**Symptoms:**
- Upload starts successfully
- Progress bar reaches ~80-90%
- Request times out

**Workaround:**
```apache
# Increase Apache timeout in Horizon
Timeout 600
ProxyTimeout 600

# Or use Nginx with longer timeouts
proxy_read_timeout 600s;
proxy_send_timeout 600s;
```

## Related Work

### Related Analyses

- **[To be populated]** - Link to any related analysis documents once created
- Integration test architecture changes
- Django 5 migration impacts

### External References

- [OpenStack Glance CORS Documentation](https://docs.openstack.org/glance/latest/admin/cors.html)
- [CORS MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Oslo Middleware CORS](https://docs.openstack.org/oslo.middleware/latest/reference/cors.html)
- [Horizon Configuration Reference](https://docs.openstack.org/horizon/latest/configuration/settings.html)

### Upstream Discussions

**[To be populated with links from github-reviewer-agent]**

- Bug reports related to direct upload
- Feature requests for CORS support
- Operator enhancement proposals

## Reproduction Steps

To replicate this research:

```bash
# Step 1: Query the github-reviewer-agent
@github-reviewer-agent please search for any work done with respect to Horizon/Glance 
and the changes made (CORS, httpd.conf, ..) to support direct mode upload by default

# Step 2: Search openstack-k8s-operators repositories
cd /home/omcgonag/Work/mymcp/workspace
git clone https://github.com/openstack-k8s-operators/horizon-operator
cd horizon-operator
git log --all --grep="direct upload" --grep="CORS" --oneline

# Step 3: Examine configuration templates
find . -name "*.yaml" -o -name "*.conf" | xargs grep -l "CORS\|direct"

# Step 4: Check OpenDev reviews
@opendev-reviewer-agent search for "direct upload" in openstack/horizon

# Step 5: Test in live environment
kubectl get horizon -n openstack
kubectl describe horizon -n openstack | grep -i direct
```

## Conclusions

### Key Takeaways

1. **Performance Benefits Are Significant**
   - Direct mode eliminates double data transfer
   - Reduces Horizon resource consumption during uploads
   - Improves user experience with faster uploads

2. **CORS Configuration Is Critical**
   - Must be configured in both Glance and Horizon
   - Browser security model requires explicit CORS approval
   - Testing CORS is essential before production deployment

3. **Multiple Components Must Be Coordinated**
   - Glance CORS middleware
   - Horizon configuration and UI changes
   - Apache/httpd proxy headers
   - Kubernetes operator templates

4. **Security Considerations**
   - CORS must be properly scoped (not wildcard with credentials)
   - HTTPS required for both Horizon and Glance
   - Auth tokens must be handled securely in browser

### Recommendations

1. ✅ **Enable Direct Mode by Default** in new deployments
   - Performance benefits outweigh complexity
   - Resource efficiency gains are substantial

2. ✅ **Test Thoroughly with Multiple Browsers**
   - Chrome, Firefox, Safari, Edge
   - Different network conditions
   - Various file sizes

3. ✅ **Monitor Horizon Resource Usage**
   - Should see reduced CPU/memory during uploads
   - Metrics validate direct mode is working

4. ✅ **Document CORS Configuration Clearly**
   - Operators need clear guidance
   - CORS errors can be confusing
   - Provide troubleshooting guide

5. ✅ **Provide Migration Path**
   - Support both proxy and direct modes
   - Allow gradual rollout
   - Easy fallback if issues arise

### Future Work

- [ ] Investigate findings from github-reviewer-agent
- [ ] Document specific PR numbers and commit SHAs
- [ ] Test direct mode in various deployment scenarios
- [ ] Create troubleshooting runbook for CORS issues
- [ ] Analyze performance metrics before/after direct mode
- [ ] Review security implications in detail
- [ ] Check for any related Jira tickets

## Appendix

### CORS Preflight Request/Response Examples

#### Successful CORS Preflight

```http
# Request
OPTIONS /v2/images HTTP/1.1
Host: glance.example.com
Origin: https://horizon.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: x-auth-token,content-type

# Response
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://horizon.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: x-auth-token, content-type
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
Content-Length: 0
```

#### Failed CORS (Missing Headers)

```http
# Response (wrong)
HTTP/1.1 200 OK
Content-Type: application/json

# Browser Console Error:
# CORS policy: No 'Access-Control-Allow-Origin' header is present
```

### Browser Console Debugging

```javascript
// Check if direct upload is enabled in Horizon
// (Run in browser console on Horizon page)
console.log("Direct Upload:", horizon.settings.GLANCE_DIRECT_UPLOAD);

// Monitor CORS preflight
performance.getEntries().filter(e => 
  e.initiatorType === 'fetch' && e.name.includes('glance')
);

// Check for CORS errors
window.addEventListener('error', function(e) {
  if (e.message.includes('CORS')) {
    console.error('CORS Error:', e);
  }
});
```

### Commands Reference

```bash
# Glance CORS Configuration Check
openstack-config --get /etc/glance/glance-api.conf cors allowed_origin
openstack-config --get /etc/glance/glance-api.conf cors allow_credentials
openstack-config --get /etc/glance/glance-api.conf cors allow_headers

# Test CORS from CLI
curl -i -X OPTIONS \
  -H "Origin: https://horizon.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Auth-Token" \
  https://glance.example.com:9292/v2/images

# Check Horizon httpd.conf
kubectl exec -n openstack horizon-pod -- cat /etc/httpd/conf.d/horizon.conf | grep -i cors

# Monitor upload in real-time
kubectl logs -n openstack -f glance-api-pod | grep -i upload

# Check resource usage during upload
kubectl top pod -n openstack --watch | grep horizon
```

---

**Status:** 🔄 **Awaiting github-reviewer-agent response**  
**Last Updated:** October 28, 2025  
**Author:** Analysis Team  
**Reviewers:** Pending completion and review
