# Analysis: Horizon/Glance Direct Mode Upload Changes

## Original Inquiry

**Date:** October 28, 2025  
**Asked to:** @github-reviewer-agent  
**Query:**
```
please search for any work done with respect to Horizon/Glance and the changes made 
(CORS, httpd.conf, ..) to support direct mode upload by default
```

## Executive Summary

This analysis investigates the implementation of direct mode upload functionality in OpenStack Horizon and Glance, focusing on:
- CORS (Cross-Origin Resource Sharing) configuration changes
- Apache httpd.conf modifications
- Direct upload vs. proxy upload modes
- Related code changes and configuration updates

**Status:** 🔄 Awaiting response from @github-reviewer-agent

---

## Data Sources

- [ ] GitHub Pull Requests (horizon-operator, openstack-k8s-operators)
- [ ] OpenDev Reviews (openstack/horizon, openstack/glance)
- [ ] Configuration changes (CORS, httpd.conf)
- [ ] Documentation updates

---

## Background: Direct Mode vs Proxy Mode

### Proxy Mode (Traditional)
In proxy mode, image uploads flow through Horizon:
```
User Browser → Horizon (Django) → Glance API → Storage Backend
```

**Drawbacks:**
- Horizon acts as intermediary, consuming resources
- Large uploads can overwhelm Horizon processes
- Memory and bandwidth intensive for Horizon server
- Slower upload speeds due to double transfer

### Direct Mode (Improved)
In direct mode, uploads go directly to Glance:
```
User Browser → Glance API (direct) → Storage Backend
```

**Benefits:**
- Reduced load on Horizon
- Faster uploads (single transfer)
- Better for large images
- More scalable

**Requirement:**
- CORS must be properly configured on Glance
- Browser security policies require CORS headers
- httpd.conf may need proxy configuration updates

---

## Detailed Findings

### GitHub Pull Requests

**[To be populated with github-reviewer-agent results]**

Search criteria:
- Repository: openstack-k8s-operators/horizon-operator
- Keywords: "direct mode", "CORS", "httpd.conf", "Glance upload"
- Related repositories: glance-operator, openstack-operator

### Configuration Changes

#### CORS Configuration

Expected changes in Glance configuration:
```ini
[cors]
allowed_origin = https://horizon.example.com
allow_credentials = true
expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token
allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token
```

#### Apache httpd.conf Changes

Expected changes for Horizon:
```apache
# Enable CORS headers for direct upload
Header set Access-Control-Allow-Origin "https://glance.example.com"
Header set Access-Control-Allow-Credentials "true"

# Proxy configuration updates
ProxyPass /api/glance http://glance-api:9292/
ProxyPassReverse /api/glance http://glance-api:9292/
```

---

## Related OpenDev Reviews

**[To be populated with findings]**

Search in:
- openstack/horizon
- openstack/glance
- openstack/glance_store

Keywords:
- "direct upload"
- "CORS"
- "direct mode"

---

## Code References

### Horizon Changes

**[To be populated]**

Expected files:
- `openstack_dashboard/dashboards/project/images/images/workflows/create_image.py`
- `openstack_dashboard/api/glance.py`
- Configuration templates

### Glance Changes

**[To be populated]**

Expected files:
- CORS configuration
- API handlers
- Documentation

### Operator Changes

**[To be populated]**

Expected files:
- `config/samples/` - Configuration templates
- `controllers/` - Operator reconciliation logic
- `templates/` - httpd.conf templates

---

## Implementation Timeline

**[To be populated with commit/PR dates]**

---

## Testing and Verification

### How to Test Direct Mode

1. **Enable direct mode** in Horizon configuration
2. **Configure CORS** in Glance
3. **Upload a test image** via Horizon UI
4. **Check browser console** for CORS errors
5. **Verify upload** goes directly to Glance (check logs)

### Verification Commands

```bash
# Check Glance CORS configuration
openstack-config --get /etc/glance/glance-api.conf cors allowed_origin

# Test CORS headers
curl -I -X OPTIONS \
  -H "Origin: https://horizon.example.com" \
  -H "Access-Control-Request-Method: POST" \
  https://glance.example.com/v2/images

# Expected response should include:
# Access-Control-Allow-Origin: https://horizon.example.com
# Access-Control-Allow-Credentials: true
```

---

## Known Issues and Workarounds

**[To be populated based on findings]**

---

## Related Analyses

- [Integration Tests Removal](../examples/opendev_reviews_open/TRACKING.md) - Related cleanup work
- [Revert 960204](../workspace/REVERT_COMPLETE_ANALYSIS.md) - Integration test code restoration

---

## Conclusions

**[To be populated after github-reviewer-agent provides information]**

### Key Takeaways

1. Direct mode upload improves performance
2. CORS configuration is critical
3. httpd.conf changes may be needed
4. Testing is essential to verify browser compatibility

### Recommendations

1. ✅ Review CORS configuration carefully
2. ✅ Test with multiple browsers
3. ✅ Monitor Horizon resource usage (should decrease)
4. ✅ Document configuration for operators
5. ✅ Provide clear upgrade path

---

## Reproduction Steps

To research this topic:

```bash
# 1. Ask github-reviewer-agent
@github-reviewer-agent please search for any work done with respect to Horizon/Glance 
and the changes made (CORS, httpd.conf, ..) to support direct mode upload by default

# 2. Search OpenDev
@opendev-reviewer-agent search for reviews related to "direct upload" and "CORS" 
in openstack/horizon and openstack/glance

# 3. Check Jira
@jiraMcp search for issues with keywords: "direct upload", "CORS", "Glance upload"

# 4. Review operator changes
@github-reviewer-agent search in openstack-k8s-operators for "direct mode" 
or "CORS" changes
```

---

## Appendix: Direct Mode Configuration Example

### Full Glance Configuration

```ini
[DEFAULT]
# ... other settings ...

[cors]
allowed_origin = https://horizon.example.com,https://horizon.alt.example.com
allow_credentials = true
expose_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token,X-OpenStack-Request-ID
allow_headers = Content-Type,Cache-Control,Content-Language,Expires,Last-Modified,Pragma,X-Auth-Token,X-Subject-Token,X-OpenStack-Request-ID
max_age = 3600
```

### Full Horizon Configuration

```python
# local_settings.py or local_settings.d/

# Enable direct upload to Glance
OPENSTACK_GLANCE_DIRECT_UPLOAD = True

# Glance endpoint for direct upload
GLANCE_ENDPOINT = 'https://glance.example.com:9292'
```

### Apache Configuration

```apache
<VirtualHost *:443>
    ServerName horizon.example.com
    
    # Enable CORS for direct uploads
    Header always set Access-Control-Allow-Origin "https://glance.example.com"
    Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
    Header always set Access-Control-Allow-Headers "Content-Type, X-Auth-Token, X-Subject-Token"
    Header always set Access-Control-Allow-Credentials "true"
    
    # ... rest of configuration ...
</VirtualHost>
```

---

**Note:** This analysis will be updated once the github-reviewer-agent provides specific findings about PRs, commits, and implementations.

**Last Updated:** October 28, 2025  
**Status:** 🔄 Awaiting github-reviewer-agent response

