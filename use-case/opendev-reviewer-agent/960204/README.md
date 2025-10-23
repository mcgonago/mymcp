# OpenDev Review 960204: Integration Test Framework Migration Analysis

**Review**: [Remove all dependencies/connections of old integration test code](https://review.opendev.org/c/openstack/horizon/+/960204)  
**Status**: MERGED  
**Changes**: +9 / -9,577 lines

## Executive Summary

This review represents a major cleanup of Horizon's integration test infrastructure, removing the deprecated Selenium WebDriver-based integration test framework in favor of the newer pytest-based testing approach. The change removed approximately 9,577 lines of legacy code while preserving the modern testing infrastructure that Jan Jasek (jjasek) developed over multiple quarters.

---

## The Old Integration Test Framework

### Overview

The old integration test framework was a comprehensive Selenium WebDriver-based testing system located at:

```
openstack_dashboard/test/integration_tests/
```

### Architecture & Design

The old framework followed a **Page Object Model** design pattern with the following structure:

#### 1. **Core Framework Components**

**Location**: `openstack_dashboard/test/integration_tests/`

| File | Purpose |
|------|---------|
| `basewebobject.py` | Base class for all web objects with common Selenium interactions |
| `basepage.py` | Base class for page objects with navigation and common page methods |
| `pageobject.py` | Enhanced page object implementation with waiting and element finding |
| `helpers.py` | Test helper functions and BaseTestCase class |
| `decorators.py` | Test decorators (`@services`, `@skip_because`, etc.) |
| `video_recorder.py` | Video recording capability for test failures |
| `config.py` | Configuration management using oslo.config |
| `horizon.conf` | Configuration file for test endpoints and credentials |

#### 2. **Page Object Model Structure**

The framework organized UI elements into reusable page objects:

```
pages/
├── admin/                      # Admin panel pages
│   ├── compute/
│   │   ├── flavorspage.py
│   │   ├── instancespage.py
│   │   └── imagespage.py
│   ├── network/
│   │   ├── networkspage.py
│   │   └── routerspage.py
│   └── volume/
│       └── volumespage.py
├── identity/                   # Identity management pages
│   ├── userspage.py
│   ├── projectspage.py
│   └── rolespage.py
└── project/                    # Project-level pages
    ├── compute/
    │   ├── instancespage.py
    │   └── imagespage.py
    └── network/
        └── networkspage.py
```

#### 3. **Reusable UI Components (Regions)**

The framework included reusable components for common UI patterns:

```
regions/
├── baseregion.py          # Base class for all UI regions
├── tables.py              # Table components and row actions
├── forms.py               # Form handling and field interactions
├── menus.py               # Navigation menu components
├── bars.py                # Progress bars and status indicators
└── messages.py            # Toast messages and notifications
```

#### 4. **Test Cases**

Comprehensive test suites covering all major Horizon functionality:

```
tests/
├── test_instances.py      # Instance create/delete/manage
├── test_volumes.py        # Volume operations
├── test_networks.py       # Network management
├── test_users.py          # User management
├── test_login.py          # Authentication tests
└── test_*                 # 20+ other test files
```

### How It Was Executed

#### Tox Environment Configuration

```ini
[testenv:integration]
passenv = DISPLAY, FFMPEG_INSTALLED, XAUTHORITY
setenv = 
    INTEGRATION_TESTS=1
    SELENIUM_HEADLESS=True
commands = 
    oslo-config-generator --namespace openstack_dashboard_integration_tests
    pytest {toxinidir}/openstack_dashboard/test/integration_tests
```

#### CI/CD Pipeline Integration

The old framework was executed via Zuul jobs:

- **Job Name**: `horizon-integration-pytest`
- **Parent**: `devstack`
- **Tox Environment**: `integration-pytest`
- **Infrastructure**: 
  - Deployed full DevStack environment
  - Ran against live OpenStack services
  - Captured screenshots on failure
  - Recorded video for debugging

#### Configuration

Tests connected to OpenStack via `horizon.conf`:

```ini
[dashboard]
dashboard_url=http://localhost/dashboard/
auth_url=http://localhost/identity/v3

[identity]
username=admin
password=secretadmin
project_name=admin
domain_name=Default
```

### Key Features

1. **Page Object Pattern**: Clean separation between test logic and UI elements
2. **Reusable Components**: Tables, forms, and menus could be reused across tests
3. **Service Decorators**: Tests could specify required OpenStack services
4. **Video Recording**: Automatic recording of failed tests for debugging
5. **Comprehensive Coverage**: Tested Admin, Project, Identity, Network, Volume, and Compute panels
6. **Screenshot Capture**: Automatic screenshots on test failures
7. **Configuration Management**: oslo.config integration for flexible test configuration

---

## The New Integration Test Framework

### Overview

The new framework, developed by Jan Jasek over multiple quarters, consists of **two separate test suites**:

1. **horizon-integration-pytest**: Modern pytest-based integration tests
2. **horizon-ui-pytest**: Pytest-based UI-specific tests

### Architecture & Design

#### 1. **horizon-integration-pytest**

**Location**: `openstack_dashboard/test/selenium/integration/`

**Purpose**: Integration testing of Horizon functionality against live OpenStack services

**Key Characteristics**:
- Uses pytest framework (modern Python testing)
- Simpler structure than old framework
- Focuses on functional integration testing
- Still uses Selenium for browser automation
- More maintainable test structure

**Test Structure**:
```
openstack_dashboard/test/selenium/integration/
├── conftest.py                    # Pytest fixtures and configuration
├── test_credentials.py
├── test_defaults.py
├── test_instances.py
├── test_volumes.py
├── test_networks.py
├── test_users.py
└── test_*                         # Other integration tests
```

#### 2. **horizon-ui-pytest**

**Location**: `openstack_dashboard/test/selenium/ui/`

**Purpose**: UI-specific testing separate from full integration testing

**Key Characteristics**:
- Focused on UI components and interactions
- Can run without full OpenStack deployment
- Faster execution than integration tests
- Tests UI behavior and JavaScript functionality

### How They Are Executed

#### Tox Environment Configuration

**For Integration Tests**:
```ini
[testenv:integration-pytest]
passenv = DISPLAY, FFMPEG_INSTALLED, XAUTHORITY
setenv = SELENIUM_HEADLESS=True
commands = 
    oslo-config-generator --namespace openstack_dashboard_integration_tests
    pytest {toxinidir}/openstack_dashboard/test/selenium/integration
```

**For UI Tests**:
```ini
[testenv:ui-pytest]
passenv = DISPLAY, FFMPEG_INSTALLED, XAUTHORITY
setenv = SELENIUM_HEADLESS=True
commands = 
    oslo-config-generator --namespace openstack_dashboard_integration_tests
    pytest {toxinidir}/openstack_dashboard/test/selenium/ui
```

#### CI/CD Pipeline Integration

**Zuul Job: horizon-integration-pytest**

```yaml
- job:
    name: horizon-integration-pytest
    parent: devstack
    nodeset: devstack-single-node-debian-bookworm
    pre-run: playbooks/horizon-devstack-integration/pre.yaml
    run: playbooks/horizon-devstack-integration/run.yaml
    post-run: playbooks/horizon-devstack-integration/post.yaml
    vars:
      tox_envlist: integration-pytest
      devstack_services:
        horizon: true
```

**Zuul Job: horizon-ui-pytest**

```yaml
- job:
    name: horizon-ui-pytest
    parent: devstack
    nodeset: devstack-single-node-debian-bookworm
    pre-run: playbooks/horizon-devstack-integration/pre.yaml
    run: playbooks/horizon-devstack-integration/run.yaml
    post-run: playbooks/horizon-devstack-integration/post.yaml
    vars:
      tox_envlist: ui-pytest
      devstack_services:
        horizon: true
```

**Pipeline Integration**:

Both jobs run in the `check` and `gate` pipelines:

```yaml
check:
  jobs:
    - horizon-integration-pytest
    - horizon-ui-pytest
    - horizon-selenium-headless
    - horizon-dsvm-tempest-plugin

gate:
  jobs:
    - horizon-integration-pytest
    - horizon-ui-pytest
    - horizon-selenium-headless
    - horizon-dsvm-tempest-plugin
```

### Key Differences from Old Framework

| Aspect | Old Framework | New Framework |
|--------|---------------|---------------|
| **Location** | `openstack_dashboard/test/integration_tests/` | `openstack_dashboard/test/selenium/integration/` and `.../ui/` |
| **Test Framework** | Custom Page Object Model | pytest-native |
| **Structure** | Complex hierarchy (pages/regions/tests) | Flat test structure |
| **Complexity** | ~100+ files, 9,500+ lines | Simplified, focused tests |
| **Maintenance** | High overhead, many abstractions | Lower overhead, direct tests |
| **Separation of Concerns** | Everything in one suite | Separate integration and UI tests |
| **Configuration** | oslo.config + horizon.conf | Simplified configuration |
| **Entry Point** | `setup.cfg` oslo.config entry | No oslo.config entry needed |

---

## What Review 960204 Removed

### Files Removed

The review removed **127 files** totaling **9,577 lines**, including:

#### 1. Core Framework Files
- `basewebobject.py`
- `basepage.py`
- `pageobject.py`
- `helpers.py`
- `decorators.py`
- `video_recorder.py`

#### 2. Page Objects
- All files in `pages/admin/`
- All files in `pages/project/`
- All files in `pages/identity/`
- All files in `pages/settings/`
- All files in `pages/network/`
- All files in `pages/volume/`

#### 3. Regions (UI Components)
- `regions/tables.py`
- `regions/forms.py`
- `regions/menus.py`
- `regions/bars.py`
- `regions/messages.py`
- `regions/baseregion.py`

#### 4. Test Cases
- 20+ test files from `tests/`
- All test data files

#### 5. Configuration and Infrastructure
- Removed `oslo.config` entry point from `setup.cfg`
- Removed `[testenv:integration]` from `tox.ini`
- Removed Zuul job definition for old integration tests
- Removed references from documentation

### What Was Preserved

The review **preserved** the modern testing infrastructure:

✅ `openstack_dashboard/test/selenium/integration/` - Modern integration tests  
✅ `openstack_dashboard/test/selenium/ui/` - Modern UI tests  
✅ `openstack_dashboard/test/integration_tests/horizon.conf` - Configuration file  
✅ `openstack_dashboard/test/integration_tests/config.py` - Configuration module  
✅ Zuul job `horizon-integration-pytest`  
✅ Zuul job `horizon-ui-pytest`  
✅ Tox environments `integration-pytest` and `ui-pytest`  

---

## Key Insights from Review Process

### Jan Jasek's Comments (Reviewer)

From the review discussion, Jan Jasek highlighted:

1. **Multiple Quarters of Work**: The new integration tests represent multiple quarters of development effort
2. **Critical Tests**: The horizon-integration-pytest and horizon-ui-pytest are "the most important tests"
3. **Clear Distinction**: 
   - `horizon-integration-pytest` = New integration pytest tests
   - `horizon-ui-pytest` = Separated UI tests
   - Anything just "integration" (old framework) can be removed
4. **Configuration Dependencies**: 
   - `horizon.conf` and `config.py` should remain (used by new tests)
   - These provide configuration for connecting to OpenStack endpoints

### Why the Migration Was Necessary

1. **Maintenance Burden**: The old Page Object Model framework was complex and hard to maintain
2. **Modern Testing Practices**: pytest is more standard in the Python ecosystem
3. **Separation of Concerns**: Splitting integration and UI tests allows for more focused testing
4. **Reduced Complexity**: The new framework has ~90% less code but maintains test coverage
5. **Better CI/CD Integration**: Simpler structure integrates better with Zuul pipelines

---

## Testing Against DevStack

### Local Development Workflow

From the notes, here's how developers test locally:

#### 1. Deploy DevStack Instance

```bash
# Create PSI instance and deploy DevStack
# Follow: https://docs.openstack.org/devstack/latest/
```

#### 2. Configure horizon.conf

Update `openstack_dashboard/test/integration_tests/horizon.conf`:

```ini
[dashboard]
# Point to your DevStack instance
dashboard_url=http://10.0.148.47/dashboard/

# Keystone endpoint
auth_url=http://10.0.148.47/identity/v3

[identity]
username=admin
password=secret  # Note: default DevStack password, not 'secretadmin'
project_name=admin
domain_name=Default
```

#### 3. Run Tests

```bash
# Clone Horizon
git clone https://github.com/openstack/horizon
cd horizon

# Run integration tests
tox -e integration-pytest

# Run UI tests
tox -e ui-pytest
```

The tests will automatically use the configuration from `horizon.conf` to connect to your DevStack instance.

---

## Conclusion

Review 960204 successfully completed the migration from the old, complex Page Object Model integration test framework to the modern, pytest-based testing approach. The change:

- **Removed**: 9,577 lines of legacy test infrastructure
- **Preserved**: Modern `horizon-integration-pytest` and `horizon-ui-pytest` frameworks
- **Maintained**: Test coverage through simpler, more maintainable tests
- **Improved**: CI/CD integration and developer workflow

This represents a significant modernization of Horizon's testing infrastructure, reducing technical debt while maintaining comprehensive test coverage.

---

## References

- **Review**: https://review.opendev.org/c/openstack/horizon/+/960204
- **Jira Ticket**: https://issues.redhat.com/browse/OSPRH-18672
- **DevStack Docs**: https://docs.openstack.org/devstack/latest/
- **Reviewer**: Jan Jasek (jjasek)
- **Author**: Owen McGonagle (omcgonag)

---

*Analysis compiled from review notes and discussions between Owen McGonagle and Jan Jasek during the review process.*

