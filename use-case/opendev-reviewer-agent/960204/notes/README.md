# Background Knowledge: Old vs New Integration Test Frameworks

> [!WARNING]
> **NOTE: Contents of this document have yet to be reviewed. Very good (highly) chance of inaccuracies, please read with a bit of caution.**

> [!NOTE]
> **NOTE: If you find an obvious discrepancy/error - please feel free to fix and update, thank you.**

This document provides detailed background information about the old and new integration test frameworks in OpenStack Horizon, explaining why the migration (review 960204) was necessary.

---

## Why This Change Was Made

The removal of the old integration test framework was necessary for several reasons:

### 1. **Maintenance Burden**
- The old framework had ~9,500 lines of code
- Complex Page Object Model required expertise to maintain
- Changes to Horizon UI required updating multiple layers (pages, regions, tests)
- High barrier to entry for new contributors

### 2. **Modern Testing Practices**
- pytest has become the Python standard
- Simpler test structure is easier to understand
- pytest fixtures are more flexible than custom decorators
- Better IDE support and tooling for pytest

### 3. **Technical Debt**
- The old framework was developed years ago
- Testing practices have evolved significantly
- Maintaining two test frameworks was wasteful
- Code duplication between old and new tests

### 4. **Separation of Concerns**
- Old framework mixed UI and integration testing
- New approach separates:
  - **Integration tests**: Test actual functionality against real OpenStack
  - **UI tests**: Test UI components and JavaScript behavior

---

## Old Framework vs. New Framework

### Old Integration Test Framework

**Architecture**: Custom Page Object Model with three-layer abstraction

```
Test Layer (tests/)
    ↓
Page Object Layer (pages/)
    ↓
Region Layer (regions/)
    ↓
Selenium WebDriver
```

**Characteristics**:
- **Lines of Code**: ~9,500 lines
- **Files**: 100+ files
- **Structure**: Deep hierarchy (tests → pages → regions → base classes)
- **Test Framework**: Custom wrapper around Selenium
- **Configuration**: oslo.config integration
- **Execution**: `tox -e integration`
- **Location**: `openstack_dashboard/test/integration_tests/`

**Example Test Structure**:
```python
# Old framework approach
class TestInstances(helpers.BaseTestCase):
    @decorators.services_required("nova", "neutron")
    def test_create_instance(self):
        instances_page = self.home_pg.go_to_compute_instancespage()
        instances_page.create_instance(name="test")
        self.assertTrue(instances_page.is_instance_present("test"))
```

**Key Features**:
- Page objects encapsulated all UI elements
- Regions provided reusable components (tables, forms, menus)
- Custom decorators for test requirements
- Video recording of test failures
- Screenshot capture on errors

### New Integration Test Framework

**Architecture**: Direct pytest-based approach with minimal abstraction

```
Test Layer (test files)
    ↓
pytest fixtures
    ↓
Selenium WebDriver
```

**Characteristics**:
- **Lines of Code**: ~1,000 lines (estimated)
- **Files**: ~25-30 test files
- **Structure**: Flat structure with pytest fixtures
- **Test Framework**: pytest with Selenium
- **Configuration**: Simple horizon.conf + config.py
- **Execution**: `tox -e integration-pytest` or `tox -e ui-pytest`
- **Location**: `openstack_dashboard/test/selenium/integration/` and `.../ui/`

**Example Test Structure**:
```python
# New framework approach
@pytest.mark.integration
def test_create_instance(login, config):
    # Direct Selenium interaction with minimal abstraction
    driver = login
    driver.find_element(By.ID, "instances__action_launch").click()
    # ... test logic ...
    assert "test-instance" in driver.page_source
```

**Key Features**:
- pytest fixtures for setup/teardown
- pytest markers for test categorization
- Minimal abstraction layer
- Direct Selenium usage where needed
- Separation of integration vs UI tests

### Comparison Table

| Aspect | Old Framework | New Framework |
|--------|---------------|---------------|
| **Size** | 100+ files, ~9,500 lines | ~30 files, ~1,000 lines |
| **Abstraction** | 3 layers (pages/regions/base) | Minimal (fixtures) |
| **Learning Curve** | High | Low |
| **Maintenance** | High | Low |
| **Test Framework** | Custom | pytest-native |
| **Test Organization** | By page object hierarchy | By test type (integration/ui) |
| **Configuration** | oslo.config | Simple config files |
| **Video Recording** | Built-in | Not yet implemented |
| **Page Objects** | Comprehensive | Minimal where needed |
| **Code Reuse** | Through classes/inheritance | Through fixtures |
| **CI/CD Job** | `horizon-integration-pytest` (old) | `horizon-integration-pytest` (new) + `horizon-ui-pytest` |

---

## What Developers Need to Know

### Running Tests Locally

**Old Way** (removed):
```bash
tox -e integration
```

**New Way** (current):
```bash
# Run integration tests (require full OpenStack)
tox -e integration-pytest

# Run UI tests (can run with minimal setup)
tox -e ui-pytest
```

### Configuration

Both old and new frameworks use `horizon.conf` for configuration:

```bash
# Edit configuration
vim openstack_dashboard/test/integration_tests/horizon.conf

# Set dashboard URL and credentials
[dashboard]
dashboard_url=http://10.0.148.47/dashboard/
auth_url=http://10.0.148.47/identity/v3

[identity]
username=admin
password=secret
```

### Test Structure

**Old Framework**: Required creating page objects
```python
# Had to create: LoginPage, InstancesPage, etc.
class InstancesPage(basepage.BasePage):
    def create_instance(self, name):
        # Complex page object implementation
        pass
```

**New Framework**: Direct test implementation
```python
# Direct pytest test
def test_instances(selenium, config):
    # Direct Selenium usage
    selenium.find_element(...)
```

---

## Benefits of the New Framework

1. **Simpler Code**: 90% reduction in code size
2. **Standard Tools**: Uses pytest, the Python standard
3. **Lower Barrier**: Easier for new contributors
4. **Better Separation**: Integration vs UI tests are separate
5. **Less Maintenance**: Fewer files to maintain
6. **Faster Development**: Less abstraction = faster test writing

---

## What Was Lost (and Why It's OK)

1. **Page Object Abstractions**: Not needed with simpler approach
2. **Video Recording**: Can be re-implemented if valuable
3. **Complex Regions**: Simplified in new framework
4. **Custom Decorators**: Replaced by pytest markers

The trade-off is worthwhile: simpler, more maintainable tests that provide the same coverage.

---

*This background information supplements the main review analysis in the parent README.md*

