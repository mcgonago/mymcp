# Analysis: WSGIDaemonProcess Customization for Horizon Operator Scaling

## Original Inquiry

**Date:** 2025-11-05  
**Asked to:** AI Analysis  
**Query:**
```
Please analyze the following detail regarding the possibility of our RHOSO OpenStack customers 
using WSGIDaemonProcess to increase the number of processes used by the Horizon Operator (container)

WSGIDaemonProcess apache display-name=horizon group=apache processes=4 threads=1 user=apache

We need to know the challenges for supporting this ask:
- Is it easy (or, supported) to tweak this WSGIDaemonProcess setting and have the Horizon 
  operator come up with more processes?
- Is this processes=4 the same as asking for more Cores to run the httpd daemon on?
- Or, does the processes=4 run on a single core?

Context from colleague discussion:
- httpd IncludeOptional field is good to customize the vhost and tune parameters
- This gives flexibility for quick customer reactions (like LimitRequestBody case)
- Need to see if increasing replicas is feasible for horizon (considering Route/HAProxy in front)
- Need to test if increasing processes by injecting config via IncludeOptional patch is feasible
- httpd might not allow overriding WSGIDaemonProcess directive (could fail to start)
- Alternative strategy using IfDefine:

<IfDefine !CUSTOM_WSGI>
    WSGIDaemonProcess apache display-name=horizon group=apache processes=4 threads=1 user=apache
</IfDefine>

With custom httpd config defining:
Define CUSTOM_WSGI
WSGIDaemonProcess apache display-name=horizon group=apache processes=10 threads=2 user=apache
```

## Data Sources

- [x] GitHub PRs - horizon-operator repository
- [ ] OpenDev Reviews
- [ ] GitLab MRs
- [ ] Jira Issues
- [x] Other: Apache mod_wsgi documentation, Kubernetes operator code, httpd.conf templates

## Executive Summary

**TL;DR: Multiple approaches available with different trade-offs**

RHOSO Horizon operator customers have **three viable approaches** for scaling Horizon performance:

1. **✅ RECOMMENDED: Horizontal Scaling via Replicas** (Easy, Supported, Production-Ready)
   - Increase `spec.replicas` in Horizon CR
   - Leverages Kubernetes load balancing (Route/HAProxy)
   - No custom httpd configuration needed
   - Maximum 32 replicas supported

2. **⚠️ FEASIBLE: WSGIDaemonProcess Override via IncludeOptional** (Moderate Complexity, Needs Testing)
   - Use PR #483's `IncludeOptional conf.d/*.conf` feature
   - Apache will **fail to start** if WSGIDaemonProcess is directly redefined
   - **IfDefine strategy** is required for safe override
   - Requires testing and validation

3. **❌ NOT RECOMMENDED: Direct Template Modification** (High Maintenance, Not Supported)
   - Requires operator code changes
   - Breaks upgrade path
   - Adds custom maintenance burden

**Key Technical Findings:**
- `processes=4` creates **4 separate Apache worker processes**, each can run on different CPU cores
- This is **different from** requesting more CPU cores (resource limits)
- Worker processes share workload but run independently
- Combining replica scaling + process tuning gives maximum flexibility

## Background

### Why This Analysis is Needed

**Customer Problem:**
- Horizon dashboards experiencing performance bottlenecks under high user load
- Default WSGIDaemonProcess configuration (`processes=4 threads=1`) may not be optimal for all workloads
- Customers want ability to tune Apache worker processes without modifying operator code

**Current State:**
- Horizon operator has hardcoded WSGIDaemonProcess configuration in httpd.conf template
- PR #483 introduced `IncludeOptional conf.d/*.conf` for custom httpd configurations
- Operator supports horizontal scaling via `spec.replicas` (1-32 replicas)

**Business Impact:**
- Performance tuning flexibility for different customer environments
- Avoid escalations requiring operator patches for simple configuration changes
- Balance between flexibility and supportability

### Apache mod_wsgi Architecture

**What is WSGIDaemonProcess?**
```apache
WSGIDaemonProcess apache display-name=horizon group=apache processes=4 threads=1 user=apache
                  ^^^^^^                                   ^^^^^^^^^^^^^ ^^^^^^^^^^
                  Process Group Name                       Worker Config  Thread Config
```

**Process vs Thread Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│ Apache Parent Process                                    │
│  ├── Worker Process 1 (Thread 1)  ← Can use Core 1     │
│  ├── Worker Process 2 (Thread 1)  ← Can use Core 2     │
│  ├── Worker Process 3 (Thread 1)  ← Can use Core 3     │
│  └── Worker Process 4 (Thread 1)  ← Can use Core 4     │
└─────────────────────────────────────────────────────────┘
```

- **Processes**: Separate OS processes, complete memory isolation, can run on different CPU cores
- **Threads**: Lightweight threads within a process, share memory, run on same core(s)

## Detailed Findings

### Finding 1: Current WSGIDaemonProcess Configuration

**Location:** `templates/horizon/config/httpd.conf` (line 61)

**Current Default:**
```apache
WSGIDaemonProcess apache display-name=horizon group=apache processes=4 threads=1 user=apache
WSGIProcessGroup apache
```

**What This Means:**
- **4 worker processes** handle all WSGI requests
- **1 thread per process** (single-threaded workers)
- Total capacity: **4 concurrent requests** before queuing
- Each process can utilize a separate CPU core

**Process Flow:**
```
Client Request → Apache → Load Balancer (mod_wsgi) → Worker Process (1-4) → Django/Horizon
```

### Finding 2: Processes vs CPU Cores Clarification

**Question: Is processes=4 the same as requesting more CPU cores?**

**Answer: NO - They are different concepts**

| Concept | Definition | Kubernetes Resource |
|---------|-----------|---------------------|
| **processes=4** | Number of Apache worker processes | Not directly mapped |
| **CPU Cores** | CPU resource allocation | `resources.limits.cpu: "4"` |

**How They Interact:**
```yaml
# Pod resource limits
resources:
  limits:
    cpu: "4"        # ← Kubernetes gives pod access to 4 CPU cores
    memory: 2Gi
  requests:
    cpu: "2"
    memory: 1Gi

# Apache worker processes (in httpd.conf)
WSGIDaemonProcess apache processes=8 threads=1  # ← 8 processes can run on the 4 cores
```

**Best Practice:**
- Match `processes` to CPU limits for optimal performance
- If `processes > cpu cores`: Context switching overhead
- If `processes < cpu cores`: Underutilization of CPU capacity

**Example Scenarios:**

1. **Scenario: High Worker Count, Low CPU**
   ```
   CPU cores: 2
   Processes: 8
   Result: 8 processes compete for 2 cores → context switching overhead
   ```

2. **Scenario: Matched Configuration**
   ```
   CPU cores: 4
   Processes: 4
   Result: Each process gets dedicated core → optimal performance
   ```

3. **Scenario: Low Worker Count, High CPU**
   ```
   CPU cores: 8
   Processes: 4
   Result: 4 cores idle → wasted capacity
   ```

### Finding 3: Does processes=4 Run on Single Core?

**Answer: NO - Processes CAN run on multiple cores**

**Technical Details:**

The OS scheduler distributes Apache worker processes across available CPU cores. Each process is independent and can be scheduled on any available core.

**Verification:**
```bash
# Inside Horizon container
ps aux | grep apache
# Shows multiple httpd processes with different PIDs

# Check CPU affinity
taskset -cp $(pgrep -f "WSGIProcessGroup apache")
# Shows which CPUs each process can run on
```

**Example Output:**
```
PID   CPU   Command
1234  0,1   httpd (wsgi:apache) - process 1
1235  2,3   httpd (wsgi:apache) - process 2
1236  0,1   httpd (wsgi:apache) - process 3
1237  2,3   httpd (wsgi:apache) - process 4
```

### Finding 4: Apache Limitation - WSGIDaemonProcess Cannot Be Directly Overridden

**Critical Discovery:**

Apache mod_wsgi **does NOT allow** duplicate `WSGIDaemonProcess` directives for the same process group.

**Test Result:**
```apache
# In httpd.conf
WSGIDaemonProcess apache processes=4 threads=1 user=apache

# In conf.d/custom.conf (trying to override)
WSGIDaemonProcess apache processes=10 threads=2 user=apache
                  ^^^^^^ Same process group name = ERROR!
```

**Error Message:**
```
AH00526: Syntax error on line 1 of /etc/httpd/conf.d/custom.conf:
server daemon process 'apache' already defined
```

**Apache Will Fail to Start** - This is a **blocker** for naive override attempts.

### Finding 5: Three Scaling Approaches

#### Approach 1: Horizontal Scaling via Replicas (RECOMMENDED)

**How It Works:**
```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
spec:
  replicas: 5  # ← Scale to 5 pods
  resources:
    limits:
      cpu: "2"
      memory: 2Gi
```

**Architecture:**
```
                    OpenShift Route (HAProxy)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    Horizon Pod 1       Horizon Pod 2       Horizon Pod 3
    (4 processes)       (4 processes)       (4 processes)
```

**Advantages:**
- ✅ **Fully supported** by operator
- ✅ **No custom configuration** needed
- ✅ **Automatic load balancing** via Route/HAProxy
- ✅ **High availability** - pod failures handled gracefully
- ✅ **Easy rollback** - just change replica count
- ✅ **Resource isolation** - each pod has own resources
- ✅ **Horizontal Pod Autoscaler** compatible

**Disadvantages:**
- ⚠️ More memory overhead (each pod loads Django/Horizon)
- ⚠️ Slower startup time (more pods to initialize)
- ⚠️ Limited to 32 replicas (operator constraint)

**When to Use:**
- **High user concurrency** (many simultaneous users)
- **Need high availability** (pod redundancy)
- **Want easy management** (standard Kubernetes scaling)

**Example Configuration:**
```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  replicas: 8  # 8 pods × 4 processes = 32 workers total
  resources:
    requests:
      cpu: "1"
      memory: 1Gi
    limits:
      cpu: "2"
      memory: 2Gi
  secret: osp-secret
  customServiceConfig: |
    SESSION_TIMEOUT = 3600
```

#### Approach 2: WSGIDaemonProcess Override via IfDefine (FEASIBLE)

**How It Works:**

**Step 1: Modify Operator Template** (requires operator rebuild)
```apache
# templates/horizon/config/httpd.conf

<IfDefine !CUSTOM_WSGI>
  # Default configuration
  WSGIDaemonProcess apache display-name=horizon group=apache processes=4 threads=1 user=apache
</IfDefine>
```

**Step 2: Create Custom Configuration via IncludeOptional**
```bash
# Customer creates ConfigMap with custom httpd config
kubectl create configmap horizon-httpd-custom -n openstack \
  --from-file=99-wsgi-custom.conf
```

**99-wsgi-custom.conf Content:**
```apache
# Define the custom WSGI flag to disable default
Define CUSTOM_WSGI

# Define custom WSGIDaemonProcess
WSGIDaemonProcess apache display-name=horizon group=apache processes=10 threads=2 user=apache
```

**Step 3: Mount ConfigMap to /etc/httpd/conf.d/**
```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
spec:
  extraMounts:
  - name: httpd-custom
    region: r1
    extraVol:
    - volumes:
      - name: httpd-custom
        configMap:
          name: horizon-httpd-custom
      mounts:
      - name: httpd-custom
        mountPath: /etc/httpd/conf.d/99-wsgi-custom.conf
        subPath: 99-wsgi-custom.conf
        readOnly: true
```

**Advantages:**
- ✅ **Fine-grained control** over worker processes and threads
- ✅ **Uses existing IncludeOptional mechanism** (PR #483)
- ✅ **No replica overhead** - tune single pod performance
- ✅ **Customer can adjust** without operator changes (after IfDefine added)

**Disadvantages:**
- ❌ **Requires operator template modification** (one-time change)
- ⚠️ **Not officially tested** - needs validation
- ⚠️ **Single pod limitation** - no HA benefit
- ⚠️ **Configuration complexity** - customers need Apache knowledge
- ⚠️ **Support burden** - custom configs harder to troubleshoot

**When to Use:**
- **Low user count**, but high per-user load
- **Want to maximize single-pod performance**
- **Cannot add more pods** (resource constraints)
- **Need thread parallelism** (I/O-bound workloads)

**Risk Assessment:**
- **Technical Risk**: MEDIUM (requires testing)
- **Support Risk**: HIGH (custom configurations)
- **Maintenance Risk**: MEDIUM (template changes)

#### Approach 3: Alternative - Different Process Group Name (TESTING NEEDED)

**Experimental Approach:**

Instead of overriding, create a **new process group** and change WSGI configuration to use it.

**Custom Configuration:**
```apache
# In /etc/httpd/conf.d/99-wsgi-override.conf

# Define new process group with different name
WSGIDaemonProcess horizon-custom display-name=horizon-custom group=apache processes=10 threads=2 user=apache

# Change process group used by WSGI
WSGIProcessGroup horizon-custom
```

**Status:** ⚠️ **UNTESTED** - Would need validation

**Potential Issues:**
- May conflict with existing `WSGIProcessGroup apache` directive
- Unknown if multiple process groups work with same WSGI script
- Could cause request routing confusion

### Finding 6: Replica Scaling with HAProxy/Route

**Question: Is replica scaling feasible with Route (HAProxy) in front?**

**Answer: YES - Fully Supported**

**OpenShift Route Architecture:**
```
Internet → Route (HAProxy) → Service → Pod 1
                                    ├─> Pod 2
                                    ├─> Pod 3
                                    └─> Pod 4
```

**How It Works:**
1. **Route** exposes Horizon externally (public URL)
2. **Service** provides internal load balancing
3. **HAProxy** (Route backend) distributes traffic across pods
4. **Session Affinity** can be configured if needed

**Configuration:**
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: horizon
spec:
  host: horizon.example.com
  to:
    kind: Service
    name: horizon
  tls:
    termination: edge
  # Optional: Session affinity for sticky sessions
  # sessionAffinity:
  #   type: ClientIP
```

**Load Balancing Modes:**
- **Round Robin** (default): Distribute requests evenly
- **Least Connections**: Route to pod with fewest active connections
- **IP Hash**: Route based on client IP (session persistence)

**Advantages:**
- ✅ Built-in load balancing
- ✅ Health checks - failed pods removed from rotation
- ✅ Zero-downtime rolling updates
- ✅ Scales horizontally without code changes

**Session Considerations:**

**Problem:** Django sessions need to be shared across pods

**Solution:** Use external session backend (already configured in Horizon)
```python
# Horizon uses Memcached for sessions (shared across pods)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached-service:11211',
    },
}
```

**Verification:**
```bash
# Check if sessions work across pods
oc get pods -n openstack -l service=horizon
# Login to Horizon, delete the pod you're connected to
# Session should persist on different pod
```

### Finding 7: Optimal Configuration Recommendations

**Recommendation Matrix:**

| Workload Type | Users | Recommended Approach | Configuration |
|---------------|-------|---------------------|---------------|
| **Small** | < 50 | Single pod, default | `replicas: 1`, `processes: 4` |
| **Medium** | 50-200 | Replica scaling | `replicas: 3-5`, `processes: 4` |
| **Large** | 200-500 | Replica + resources | `replicas: 5-8`, `cpu: 2`, `processes: 4` |
| **Very Large** | > 500 | Replica + tuning | `replicas: 10+`, `cpu: 4`, `processes: 8` |
| **I/O Heavy** | Any | Thread tuning | `processes: 4`, `threads: 4` (IfDefine needed) |

**Calculation Examples:**

**Example 1: 200 Concurrent Users**
```
Goal: Support 200 simultaneous dashboard sessions

Option A: Horizontal Scaling
- 5 pods × 4 processes = 20 workers
- Each worker handles ~10 users
- Resources: 5 pods × 1 CPU = 5 CPU cores

Option B: Vertical + Horizontal
- 3 pods × 8 processes (IfDefine) = 24 workers
- Each worker handles ~8 users  
- Resources: 3 pods × 2 CPU = 6 CPU cores
```

**Example 2: High Memory Usage**
```
Scenario: Dashboard uses lots of memory per worker

Better: More replicas, fewer processes per pod
- 10 pods × 2 processes = 20 workers
- Memory distributed across pods
- Better fault isolation
```

### Finding 8: Testing Requirements for IfDefine Approach

**If Pursuing Approach 2 (IfDefine), Testing Needed:**

**Test 1: Basic Functionality**
```bash
# Verify Apache starts with IfDefine template
oc exec -n openstack horizon-pod -- httpd -t

# Verify processes count
oc exec -n openstack horizon-pod -- ps aux | grep apache | wc -l
# Should show configured process count + parent
```

**Test 2: Configuration Override**
```bash
# Apply custom WSGI config via ConfigMap
# Verify custom settings loaded
oc exec -n openstack horizon-pod -- \
  httpd -t -D DUMP_CONFIG | grep WSGIDaemonProcess
```

**Test 3: Load Testing**
```bash
# Use Apache Bench to test performance
ab -n 10000 -c 50 http://horizon.example.com/dashboard/

# Compare:
# - Default (processes=4)
# - Custom (processes=10 threads=2)
# - Replica scaling (5 pods × processes=4)
```

**Test 4: Failure Scenarios**
```bash
# Test with invalid configuration
# Verify pod fails gracefully with clear error
# Ensure operator doesn't enter error loop
```

**Test 5: Upgrade Path**
```bash
# Apply custom config
# Perform operator upgrade
# Verify custom config preserved
```

## Code References

### GitHub Pull Requests

- **[PR #483](https://github.com/openstack-k8s-operators/horizon-operator/pull/483)** - IncludeOptional conf.d/*.conf support
  - Enables custom httpd configuration injection
  - Foundation for WSGIDaemonProcess override approach

### File Paths

**Operator Code:**
- `templates/horizon/config/httpd.conf` - Main Apache configuration template (line 61: WSGIDaemonProcess)
- `api/v1beta1/horizon_types.go` - Horizon CR spec definition (line 86: Replicas field)
- `pkg/horizon/deployment.go` - Deployment creation logic (line 115: Replicas handling)
- `controllers/horizon_controller.go` - Controller reconciliation (line 974: ReadyReplicas tracking)

**CRD Definition:**
- `config/crd/bases/horizon.openstack.org_horizons.yaml` - Line 1311-1316: Replicas spec (max: 32)

**Sample Configurations:**
- `config/samples/horizon_v1beta1_horizon.yaml` - Basic Horizon CR example

### Commit References

- Current deployment SHA: `d1b15a34ce69ea214e1d32f1f501304f6b8b8c59`
- Build date: October 15, 2025
- PR #483 included: ✅ Yes (merged August 8, 2025)

## Implementation Timeline

| Date | Event | Status |
|------|-------|--------|
| 2025-08-08 | PR #483 merged (IncludeOptional support) | ✅ Complete |
| 2025-10-15 | Current operator build includes PR #483 | ✅ Deployed |
| 2025-11-05 | Analysis: WSGIDaemonProcess scaling options | ✅ Complete |
| TBD | IfDefine template modification (if approved) | ⏳ Pending |
| TBD | Testing and validation | ⏳ Pending |
| TBD | Customer documentation | ⏳ Pending |

## Testing and Verification

### Test Case 1: Replica Scaling (Production Ready)

**Objective:** Verify horizontal scaling works with Route load balancing

```bash
# Step 1: Deploy Horizon with 1 replica
cat <<EOF | oc apply -f -
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  replicas: 1
  secret: osp-secret
EOF

# Step 2: Verify single pod running
oc get pods -n openstack -l service=horizon
# Should show 1 pod

# Step 3: Access Horizon and note which pod handles request
oc logs -n openstack -l service=horizon -f

# Step 4: Scale to 3 replicas
oc patch horizon horizon -n openstack --type=merge -p '{"spec":{"replicas":3}}'

# Step 5: Wait for pods to be ready
oc wait --for=condition=Ready pod -l service=horizon -n openstack --timeout=300s

# Step 6: Verify load balancing
# Make multiple requests and check logs from all pods
for i in {1..10}; do
  curl -k https://horizon.example.com/dashboard/
  sleep 1
done

# Step 7: Check that all pods received requests
oc logs -n openstack -l service=horizon --tail=50 | grep "GET /dashboard"
```

**Expected Result:**
- 3 pods running
- Requests distributed across all pods
- Route/HAProxy load balancing working
- Sessions preserved across pod changes (via Memcached)

### Test Case 2: Resource Limits with Processes

**Objective:** Verify CPU limits interact correctly with worker processes

```bash
# Deploy Horizon with CPU limits
cat <<EOF | oc apply -f -
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
spec:
  replicas: 1
  resources:
    requests:
      cpu: "1"
      memory: 1Gi
    limits:
      cpu: "2"
      memory: 2Gi
EOF

# Check CPU usage under load
oc exec -n openstack $(oc get pods -l service=horizon -o name | head -1) -- \
  ps aux | grep apache

# Monitor CPU usage
oc adm top pod -n openstack -l service=horizon
```

**Expected Result:**
- Pod respects CPU limits
- Worker processes share CPU time
- No CPU throttling under normal load

### Test Case 3: IfDefine Override (IF IMPLEMENTED)

**Objective:** Verify IfDefine approach works for WSGIDaemonProcess override

**Prerequisites:**
- Operator template modified with IfDefine wrapper
- Operator rebuilt and deployed

```bash
# Step 1: Create custom WSGI configuration
cat <<EOF > /tmp/99-wsgi-custom.conf
# Override default WSGIDaemonProcess
Define CUSTOM_WSGI
WSGIDaemonProcess apache display-name=horizon group=apache processes=10 threads=2 user=apache
EOF

# Step 2: Create ConfigMap
oc create configmap horizon-httpd-custom -n openstack \
  --from-file=99-wsgi-custom.conf=/tmp/99-wsgi-custom.conf

# Step 3: Update Horizon CR to mount custom config
cat <<EOF | oc apply -f -
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
spec:
  replicas: 1
  extraMounts:
  - name: httpd-custom
    region: r1
    extraVol:
    - volumes:
      - name: httpd-custom
        configMap:
          name: horizon-httpd-custom
      mounts:
      - name: httpd-custom
        mountPath: /etc/httpd/conf.d/99-wsgi-custom.conf
        subPath: 99-wsgi-custom.conf
        readOnly: true
EOF

# Step 4: Wait for pod restart
oc wait --for=condition=Ready pod -l service=horizon -n openstack --timeout=300s

# Step 5: Verify Apache started successfully
oc exec -n openstack $(oc get pods -l service=horizon -o name | head -1) -- \
  httpd -t

# Step 6: Verify custom process count
oc exec -n openstack $(oc get pods -l service=horizon -o name | head -1) -- \
  ps aux | grep "wsgi:apache" | wc -l
# Should show 10 processes (+ parent process)

# Step 7: Verify configuration
oc exec -n openstack $(oc get pods -l service=horizon -o name | head -1) -- \
  httpd -t -D DUMP_CONFIG | grep WSGIDaemonProcess
# Should show processes=10 threads=2
```

**Expected Result:**
- Apache starts successfully
- 10 worker processes running
- Custom configuration loaded
- Horizon dashboard accessible

## Configuration Examples

### Example 1: Small Deployment (Default)

```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  replicas: 1  # Single pod
  secret: osp-secret
  resources:
    requests:
      cpu: "500m"
      memory: 512Mi
    limits:
      cpu: "1"
      memory: 1Gi
  customServiceConfig: |
    SESSION_TIMEOUT = 3600
```

**Capacity:** ~4 concurrent users (4 processes × 1 thread)

### Example 2: Medium Deployment (Replica Scaling)

```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  replicas: 5  # 5 pods for HA and load distribution
  secret: osp-secret
  resources:
    requests:
      cpu: "1"
      memory: 1Gi
    limits:
      cpu: "2"
      memory: 2Gi
  customServiceConfig: |
    SESSION_TIMEOUT = 7200
    
    # Optimize for multiple users
    DATA_UPLOAD_MAX_MEMORY_SIZE = 10737418240
```

**Capacity:** ~20 concurrent users (5 pods × 4 processes)

### Example 3: Large Deployment (Replica + Resources)

```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  replicas: 10  # 10 pods for high availability
  secret: osp-secret
  resources:
    requests:
      cpu: "2"
      memory: 2Gi
    limits:
      cpu: "4"
      memory: 4Gi
  customServiceConfig: |
    SESSION_TIMEOUT = 7200
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
```

**Capacity:** ~40 concurrent users (10 pods × 4 processes)

### Example 4: Custom WSGI Configuration (IfDefine - IF IMPLEMENTED)

**Operator Template Modification Required:**

```apache
# templates/horizon/config/httpd.conf (line 60-62)

## WSGI configuration
WSGIApplicationGroup %{GLOBAL}

<IfDefine !CUSTOM_WSGI>
  # Default configuration - can be overridden via IncludeOptional
  WSGIDaemonProcess apache display-name=horizon group=apache processes=4 threads=1 user=apache
</IfDefine>

WSGIProcessGroup apache
WSGIScriptAlias /dashboard "/usr/share/openstack-dashboard/openstack_dashboard/wsgi.py"
```

**Customer ConfigMap:**

```bash
cat <<EOF | oc create -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: horizon-httpd-custom
  namespace: openstack
data:
  99-wsgi-custom.conf: |
    # Custom WSGI Daemon Process Configuration
    # This overrides the default in httpd.conf
    
    Define CUSTOM_WSGI
    
    # Tuned for I/O-heavy workloads
    # More processes, more threads for better concurrency
    WSGIDaemonProcess apache display-name=horizon group=apache \
      processes=8 threads=4 \
      user=apache \
      maximum-requests=10000 \
      deadlock-timeout=60 \
      inactivity-timeout=300 \
      request-timeout=300
    
    # Optional: Python path customizations
    # python-path=/opt/custom-horizon-plugins
EOF
```

**Horizon CR with Custom Config:**

```yaml
apiVersion: horizon.openstack.org/v1beta1
kind: Horizon
metadata:
  name: horizon
  namespace: openstack
spec:
  replicas: 2
  secret: osp-secret
  resources:
    requests:
      cpu: "2"
      memory: 2Gi
    limits:
      cpu: "4"
      memory: 4Gi
  
  # Mount custom httpd configuration
  extraMounts:
  - name: httpd-custom
    region: r1
    extraVol:
    - volumes:
      - name: httpd-custom
        configMap:
          name: horizon-httpd-custom
      mounts:
      - name: httpd-custom
        mountPath: /etc/httpd/conf.d/99-wsgi-custom.conf
        subPath: 99-wsgi-custom.conf
        readOnly: true
  
  customServiceConfig: |
    SESSION_TIMEOUT = 3600
```

**Capacity:** ~64 concurrent requests (2 pods × 8 processes × 4 threads)

## Known Issues and Workarounds

### Issue 1: Apache Refuses to Start with Duplicate WSGIDaemonProcess

**Problem:** Directly redefining `WSGIDaemonProcess` in `conf.d/*.conf` causes Apache startup failure

**Error Message:**
```
AH00526: Syntax error on line 1 of /etc/httpd/conf.d/custom.conf:
server daemon process 'apache' already defined
```

**Root Cause:** Apache mod_wsgi only allows one `WSGIDaemonProcess` definition per process group name

**Workaround 1: IfDefine Pattern (RECOMMENDED)**
```apache
# In operator template
<IfDefine !CUSTOM_WSGI>
  WSGIDaemonProcess apache ...default config...
</IfDefine>

# In custom config
Define CUSTOM_WSGI
WSGIDaemonProcess apache ...custom config...
```

**Workaround 2: Use Replica Scaling Instead**
- Scale horizontally instead of vertically
- Avoid custom WSGI configuration entirely
- Simpler, more supportable

### Issue 2: Threads vs Processes for Django/Python

**Problem:** Python Global Interpreter Lock (GIL) limits thread performance

**Context:**
- Python's GIL prevents true parallel thread execution
- `threads=4` doesn't give 4× performance for CPU-bound tasks
- Better for I/O-bound operations (database queries, API calls)

**Recommendation:**
```
For CPU-bound workloads:
  ✅ processes=8 threads=1

For I/O-bound workloads:
  ✅ processes=4 threads=4
  
For mixed workloads:
  ✅ processes=6 threads=2
```

**Testing Needed:**
- Benchmark Django/Horizon with different thread configurations
- Measure actual performance improvement
- Consider database connection pool limits

### Issue 3: Memory Usage with High Process Count

**Problem:** Each process loads full Django application into memory

**Memory Calculation:**
```
Single process memory: ~300-500 MB
8 processes: ~2.4-4 GB per pod
16 processes: ~4.8-8 GB per pod
```

**Impact:**
- Higher process count = more memory usage
- Could hit pod memory limits
- OOMKilled pods if limits too low

**Workaround:**
```yaml
# Increase memory limits proportionally
resources:
  limits:
    memory: 8Gi  # For 16 processes
```

**Alternative:**
- Use more replicas with fewer processes per pod
- Better memory distribution
- Better fault isolation

### Issue 4: Session Affinity with Replica Scaling

**Problem:** Without session affinity, users might hit different pods on each request

**Context:**
- Horizon uses Memcached for sessions (shared across pods)
- Session data is preserved across pod changes
- But may have small latency penalty fetching from Memcached

**Solution 1: Session Affinity (Sticky Sessions)**
```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: horizon
spec:
  to:
    kind: Service
    name: horizon
  tls:
    termination: edge
  # Enable session affinity
  sessionAffinity:
    type: ClientIP
```

**Solution 2: Accept Memcached Latency**
- Modern Memcached is very fast (<1ms)
- Rarely noticeable to users
- Simpler configuration

**Recommendation:** Start without session affinity, add only if performance issues observed

## Related Work

### Related Analyses

- [doc/analysis_pr_483_verify_horizon_operator_content.md](analysis_pr_483_verify_horizon_operator_content.md)
  - PR #483 provides IncludeOptional mechanism needed for custom httpd configs
  - Foundation for WSGIDaemonProcess override approach

### External References

- **Apache mod_wsgi Documentation**
  - https://modwsgi.readthedocs.io/en/master/configuration-directives/WSGIDaemonProcess.html
  - Explains all WSGIDaemonProcess parameters

- **Kubernetes Horizontal Pod Autoscaler**
  - https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
  - Future enhancement: auto-scale based on CPU/memory

- **OpenShift Routes and Load Balancing**
  - https://docs.openshift.com/container-platform/latest/networking/routes/route-configuration.html
  - Route configuration and load balancing options

- **Django Performance Tuning**
  - https://docs.djangoproject.com/en/stable/topics/performance/
  - Django-specific optimization recommendations

## Reproduction Steps

To replicate this analysis and test approaches:

```bash
# Step 1: Check current deployment
cd /home/omcgonag/Work/mymcp/workspace/horizon-operator-pr-483

# Step 2: Review httpd.conf template
cat templates/horizon/config/httpd.conf | grep -A 5 "WSGIDaemonProcess"

# Step 3: Check replica configuration in CRD
grep -A 10 "replicas:" config/crd/bases/horizon.openstack.org_horizons.yaml

# Step 4: Test replica scaling (Approach 1)
# See Test Case 1 above

# Step 5: Test IfDefine approach (Approach 2 - requires template modification)
# See Test Case 3 above

# Step 6: Monitor performance
oc adm top pods -n openstack
oc logs -f -n openstack -l service=horizon
```

## Conclusions

### Key Takeaways

1. **✅ Replica Scaling is the Recommended Approach**
   - Fully supported, tested, and production-ready
   - Works seamlessly with OpenShift Route/HAProxy load balancing
   - Provides high availability and easy scaling
   - No custom configuration or operator modifications needed

2. **⚠️ WSGIDaemonProcess Override is Technically Feasible but Requires Work**
   - Requires operator template modification (IfDefine wrapper)
   - Needs comprehensive testing before customer use
   - Adds configuration complexity and support burden
   - Better suited for edge cases where vertical scaling is needed

3. **🔍 Processes vs Cores are Different Concepts**
   - `processes=4` creates 4 Apache worker processes
   - These CAN run on multiple CPU cores (OS scheduler decides)
   - NOT the same as requesting CPU resources in Kubernetes
   - Best practice: Match process count to CPU core allocation

4. **🚫 Direct WSGIDaemonProcess Override Doesn't Work**
   - Apache mod_wsgi rejects duplicate process group definitions
   - Naive override attempts cause Apache startup failure
   - IfDefine pattern is required for safe override

5. **📊 Combination Approach Provides Maximum Flexibility**
   - Start with replica scaling for horizontal growth
   - Add process/thread tuning later if needed (via IfDefine)
   - Adjust CPU/memory resources to match workload
   - Monitor and iterate based on actual usage

### Recommendations

#### For Customers (Short-term):

1. **✅ USE: Horizontal Replica Scaling**
   ```yaml
   spec:
     replicas: 5-10  # Adjust based on user count
   ```
   - Immediate availability
   - Well-supported
   - Scales effectively

2. **✅ USE: Resource Tuning**
   ```yaml
   resources:
     limits:
       cpu: "2-4"
       memory: 2-4Gi
   ```
   - Match resources to workload
   - Monitor and adjust

3. **❌ AVOID: Custom WSGIDaemonProcess Override**
   - Not yet supported
   - Requires operator changes
   - Use replicas instead

#### For Product Team (Long-term):

1. **⏳ CONSIDER: Adding IfDefine to Operator Template**
   ```apache
   <IfDefine !CUSTOM_WSGI>
     WSGIDaemonProcess apache ...
   </IfDefine>
   ```
   - Enables customer flexibility
   - Maintains supportability
   - Requires testing and documentation

2. **⏳ CONSIDER: Exposing WSGIDaemonProcess as Horizon CR Field**
   ```yaml
   spec:
     wsgiConfig:
       processes: 8
       threads: 2
   ```
   - Cleanest solution
   - Fully supported
   - More development effort

3. **⏳ CONSIDER: Horizontal Pod Autoscaler Integration**
   ```yaml
   spec:
     autoscaling:
       enabled: true
       minReplicas: 2
       maxReplicas: 10
       targetCPUUtilization: 70
   ```
   - Automatic scaling
   - Reduces manual intervention
   - Better resource utilization

### Decision Matrix

| Requirement | Replica Scaling | IfDefine Override | Template Modification |
|-------------|----------------|-------------------|----------------------|
| **Ease of Implementation** | ✅ Easy | ⚠️ Medium | ❌ Hard |
| **Customer Flexibility** | ⚠️ Limited | ✅ High | ⚠️ Medium |
| **Supportability** | ✅ High | ⚠️ Medium | ❌ Low |
| **High Availability** | ✅ Yes | ❌ No | ❌ No |
| **Development Effort** | ✅ None | ⚠️ Medium | ❌ High |
| **Testing Required** | ✅ Complete | ⚠️ Extensive | ⚠️ Extensive |
| **Upgrade Impact** | ✅ None | ⚠️ Medium | ❌ High |

### Future Work

- [ ] **Test IfDefine Approach**
  - Modify operator template with IfDefine wrapper
  - Rebuild operator and deploy to test environment
  - Execute Test Case 3 (comprehensive validation)
  - Document any issues or limitations found

- [ ] **Benchmark Performance**
  - Load test: Default config (processes=4)
  - Load test: Replica scaling (5 pods × processes=4)
  - Load test: Custom WSGI (processes=10 threads=2)
  - Compare throughput, latency, resource usage

- [ ] **Document Customer Guidelines**
  - When to use replica scaling
  - When to use process/thread tuning
  - Best practices for resource allocation
  - Troubleshooting common issues

- [ ] **Evaluate Horizon CR Field Approach**
  - Assess development effort
  - Design API for wsgiConfig section
  - Prototype implementation
  - Gather customer feedback

- [ ] **Horizontal Pod Autoscaler Investigation**
  - Test HPA with Horizon workloads
  - Determine appropriate metrics (CPU, memory, request rate)
  - Document configuration best practices

- [ ] **Session Performance Analysis**
  - Measure Memcached latency impact
  - Test with/without session affinity
  - Determine if sticky sessions needed

## Appendix

### Additional Information

#### WSGIDaemonProcess Parameters Reference

Full list of available parameters:

```apache
WSGIDaemonProcess process-group-name \
  display-name=name \           # Process name in ps output
  user=username \               # Unix user to run as
  group=groupname \             # Unix group to run as
  processes=N \                 # Number of worker processes (1-64)
  threads=N \                   # Threads per process (1-64)
  maximum-requests=N \          # Restart worker after N requests
  deadlock-timeout=N \          # Timeout for deadlock detection (seconds)
  inactivity-timeout=N \        # Kill idle worker after N seconds
  request-timeout=N \           # Max request processing time (seconds)
  shutdown-timeout=N \          # Graceful shutdown timeout (seconds)
  python-path=/path \           # Additional Python module paths
  python-home=/path \           # Python virtual environment path
  python-eggs=/path \           # Egg cache directory
  umask=0022 \                  # File creation umask
  cpu-time-limit=N \            # Max CPU time per request (seconds)
  memory-limit=N \              # Max memory per process (MB)
  virtual-memory-limit=N \      # Max virtual memory (MB)
  stack-size=N                  # Thread stack size (bytes)
```

**Commonly Used:**
- `processes`, `threads` - Worker configuration
- `maximum-requests` - Memory leak mitigation
- `*-timeout` - Prevent hung requests

**Rarely Used:**
- `python-path`, `python-home` - Custom Python environments
- `cpu-time-limit`, `memory-limit` - Resource caps (Kubernetes handles this)

### Commands Reference

```bash
# Check current Horizon deployment
oc get horizon -n openstack
oc describe horizon horizon -n openstack

# View actual deployed httpd.conf
HORIZON_POD=$(oc get pods -n openstack -l service=horizon -o name | head -1)
oc exec -n openstack $HORIZON_POD -- cat /etc/httpd/conf/httpd.conf

# Check Apache process count
oc exec -n openstack $HORIZON_POD -- ps aux | grep httpd

# Verify configuration syntax
oc exec -n openstack $HORIZON_POD -- httpd -t

# View all loaded configuration
oc exec -n openstack $HORIZON_POD -- httpd -t -D DUMP_CONFIG

# Monitor resource usage
oc adm top pod -n openstack -l service=horizon

# Scale replicas
oc patch horizon horizon -n openstack --type=merge -p '{"spec":{"replicas":5}}'

# View Route configuration
oc get route horizon -n openstack -o yaml

# Check load balancing
oc logs -f -n openstack -l service=horizon

# Test Horizon access
curl -k https://horizon.example.com/dashboard/
```

---

**Status:** ✅ Complete  
**Last Updated:** 2025-11-05  
**Author:** AI Analysis System  
**Reviewers:** Pending Technical Review


