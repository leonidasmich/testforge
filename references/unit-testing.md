# Unit Testing Guidelines

## 1. Test Isolation & Test Doubles
Unit tests must run in strict isolation. Select test doubles according to Google SWE guidelines:
- **Fakes**: Lightweight, working in-memory implementations (e.g., `InMemRepository`). Preferred over mocks.
- **Stubs**: Fixed responses to specific calls. Use for simple input/output mapping.
- **Mocks**: Interaction verifiers. Use ONLY when state cannot be observed directly (e.g., verifying an email alert was sent).

## 2. Framework Guidelines

### Python (Pytest)
```python
import pytest
from myapp.service import CalculatorService

def test_divide_by_positive_number_returns_correct_quotient():
    # Arrange
    calc = CalculatorService()
    
    # Act
    result = calc.divide(10, 2)
    
    # Assert
    assert result == 5.0

def test_divide_by_zero_raises_value_error():
    calc = CalculatorService()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(10, 0)


JavaScript/TypeScript (Jest/Vitest)

import { UserService } from '../src/user-service';

describe('UserService', () => {
  it('should calculate active user count correctly', () => {
    // Arrange
    const users = [
      { id: 1, active: true },
      { id: 2, active: false },
      { id: 3, active: true }
    ];
    const service = new UserService(users);

    // Act
    const count = service.getActiveCount();

    // Assert
    expect(count).toBe(2);
  });
});


Java (JUnit 5)

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DiscountCalculatorTest {
    @Test
    void shouldApplyTenPercentDiscountForVIPCustomers() {
        DiscountCalculator calc = new DiscountCalculator();
        double finalPrice = calc.calculate(100.0, CustomerType.VIP);
        assertEquals(90.0, finalPrice, 0.001);
    }
}

