# Multi-Agent System - Agents Module

## Overview

This module implements a complete multi-agent system for Munder Difflin Paper Company using specialized AI agents that coordinate to handle inventory management, quote generation, and order fulfillment.

## Architecture

### Agent Hierarchy

```
BaseAgent (Abstract)
├── InventoryAgent      - Inventory management and procurement
├── QuotingAgent        - Quote generation and pricing
├── FulfillmentAgent    - Order fulfillment and allocation
└── OrchestratorAgent   - Workflow coordination
```

## Components

### Core Classes

#### `BaseAgent` (`base.py`)
Abstract base class providing common functionality for all agents:

- **Initialization**: Name, model, system prompt, logger
- **Logging**: Structured logging with `_log_start()`, `_log_complete()`
- **Error Handling**: Consistent error handling with `_handle_error()`
- **Tool Registration**: Integration with pydantic-ai tools
- **Abstract Methods**: `process()` must be implemented by subclasses

#### `AgentProtocol` (`base.py`)
Protocol defining the interface all agents must implement for type safety.

### Specialized Agents

#### `InventoryAgent` (`inventory.py`)
Manages inventory levels and procurement decisions.

**Tools:**
- `check_inventory(item_name, quantity, request_date)` - Check availability
- `get_available_inventory(request_date)` - Get all inventory
- `calculate_reorder_quantity(item_name)` - Calculate reorder needs
- `get_supplier_eta(quantity, request_date)` - Get delivery estimates
- `get_low_stock_items()` - Get items needing reorder

**Use Case:** Checking if items are in stock and determining reorder needs.

#### `QuotingAgent` (`quoting.py`)
Generates price quotes with bulk discounts.

**Tools:**
- `generate_quote(items, customer_id, request_date, notes)` - Generate quotes
- `search_quotes(search_terms)` - Search historical quotes
- `calculate_discount(quantity, unit_price)` - Calculate bulk discounts
- `validate_quote(quote_id)` - Validate quote validity

**Discount Tiers:**
- 5% for orders ≥ 1,000 units
- 10% for orders ≥ 5,000 units
- 15% for orders ≥ 10,000 units

**Use Case:** Providing price quotes with appropriate discounts.

#### `FulfillmentAgent` (`fulfillment.py`)
Processes orders and manages inventory allocation.

**Tools:**
- `fulfill_order(items, customer_id, request_date, quote_id)` - Process orders
- `allocate_inventory(items)` - Allocate inventory
- `create_backorder(item_name, quantity, expected_date)` - Create backorders
- `record_transaction(item_name, quantity, price, date)` - Record sales
- `trigger_reorder(item_name, quantity)` - Trigger reorders

**Order Statuses:**
- `COMPLETED` - All items fulfilled immediately
- `PARTIAL` - Some items fulfilled, some on backorder
- `PENDING` - All items on backorder

**Use Case:** Fulfilling orders and managing backorders.

#### `OrchestratorAgent` (`orchestrator.py`)
Coordinates all specialized agents to handle complete customer workflows.

**Workflow:**
1. Parse customer request (using LLM)
2. Check inventory availability
3. Generate price quote
4. Process order (if `auto_fulfill=True`)
5. Format professional response

**Use Case:** End-to-end processing of customer requests.

## System Prompts

All agents have carefully crafted system prompts in the `prompts/` directory:

- `inventory_prompts.py` - Inventory agent prompts
- `quoting_prompts.py` - Quoting agent prompts
- `fulfillment_prompts.py` - Fulfillment agent prompts
- `orchestrator_prompts.py` - Orchestrator agent prompts

These prompts define agent personality, capabilities, and guidelines.

## Usage

### Basic Agent Creation

```python
from multi_agent_system.services import InventoryService
from multi_agent_system.agents import InventoryAgent

# Create service (with repository)
inventory_service = InventoryService(inventory_repo)

# Create agent
inventory_agent = InventoryAgent(
    inventory_service=inventory_service,
    model="openai:gpt-4o-mini"
)

# Process request
result = inventory_agent.process({
    "item_name": "A4 paper",
    "quantity": 1000,
    "request_date": "2025-01-15T10:00:00"
})

print(f"Available: {result['available']}")
print(f"Current Stock: {result['current_stock']}")
```

### Using the Orchestrator

```python
from multi_agent_system.agents import (
    OrchestratorAgent,
    InventoryAgent,
    QuotingAgent,
    FulfillmentAgent
)

# Create specialized agents
inventory_agent = InventoryAgent(inventory_service)
quoting_agent = QuotingAgent(quoting_service)
fulfillment_agent = FulfillmentAgent(fulfillment_service)

# Create orchestrator
orchestrator = OrchestratorAgent(
    inventory_agent=inventory_agent,
    quoting_agent=quoting_agent,
    fulfillment_agent=fulfillment_agent
)

# Process customer request
result = orchestrator.process({
    "request": "I need 5000 reams of A4 paper and 2000 boxes of pens",
    "customer_id": "CUST-001",
    "request_date": "2025-01-15T10:00:00",
    "auto_fulfill": True
})

# Access results
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print(f"Quote ID: {result['quote']['quote_id']}")
print(f"Total: ${result['quote']['total_amount']:.2f}")
print(f"Order Status: {result['fulfillment']['status']}")
```

### Using the Factory Function

```python
from multi_agent_system.agents import create_agent

# Create agent by type
agent = create_agent("inventory", {
    "inventory_service": inventory_service,
    "model": "openai:gpt-4o-mini"
})
```

## Integration with Services

Each agent integrates with its corresponding service layer:

```
InventoryAgent → InventoryService → InventoryRepository → Database
QuotingAgent → QuotingService → QuoteRepository → Database
FulfillmentAgent → FulfillmentService → TransactionRepository → Database
```

This architecture provides:
- **Separation of Concerns**: Agents handle AI/LLM logic, services handle business logic
- **Testability**: Services can be mocked for testing
- **Maintainability**: Business logic changes don't affect agent implementations

## Tool Registration Pattern

Tools are registered using pydantic-ai's decorator pattern:

```python
def _register_tools(self) -> None:
    """Register agent tools."""
    
    @self._agent.tool
    def check_inventory(item_name: str, quantity: int) -> dict[str, Any]:
        """
        Check inventory availability.
        
        Args:
            item_name: Name of the item
            quantity: Quantity needed
            
        Returns:
            Dictionary with availability information
        """
        result = self.service.check_availability(item_name, quantity)
        return result.model_dump()
```

This allows the LLM to:
1. Discover available tools
2. Understand tool parameters and return types
3. Call tools during agent processing
4. Receive structured responses

## Error Handling

All agents implement consistent error handling:

```python
def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
    self._log_start(input_data)
    try:
        # Processing logic
        result = self._do_processing(input_data)
        self._log_complete(result)
        return result
    except Exception as e:
        return self._handle_error(e)
```

Error responses have a standard structure:
```python
{
    "error": "Error message",
    "agent": "agent_name",
    "success": False
}
```

## Logging

All agents use structured logging via `structlog`:

```python
# Start logging
self.logger.info(
    "Agent processing started",
    agent=self.name,
    input_keys=list(input_data.keys())
)

# Completion logging
self.logger.info(
    "Agent processing completed",
    agent=self.name,
    result_keys=list(result.keys())
)

# Error logging
self.logger.exception(
    "Agent processing failed",
    agent=self.name,
    error=str(error)
)
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for LLM functionality
- `OPENAI_MODEL` - Model to use (default: "openai:gpt-4o-mini")
- `LOG_LEVEL` - Logging level (default: "INFO")

### Model Selection

Different models can be configured per agent:

```python
inventory_agent = InventoryAgent(
    inventory_service=service,
    model="openai:gpt-4"  # Use GPT-4 for this agent
)
```

## Testing

### Unit Testing

Test agents with mocked services:

```python
def test_inventory_agent_check_availability(mock_service):
    # Arrange
    mock_service.check_availability.return_value = InventoryCheckResult(
        item_name="A4 paper",
        current_stock=1000,
        available=True,
        ...
    )
    
    agent = InventoryAgent(mock_service)
    
    # Act
    result = agent.process({
        "item_name": "A4 paper",
        "quantity": 100,
        "request_date": "2025-01-15T10:00:00"
    })
    
    # Assert
    assert result["available"] is True
    assert result["success"] is True
```

### Integration Testing

Test agent coordination through orchestrator:

```python
def test_orchestrator_full_workflow(db_session):
    # Arrange - set up services with real database
    orchestrator = create_orchestrator(db_session)
    
    # Act
    result = orchestrator.process({
        "request": "I need 1000 reams of A4 paper",
        "customer_id": "TEST-001",
        "auto_fulfill": True
    })
    
    # Assert
    assert result["success"] is True
    assert "quote" in result
    assert "fulfillment" in result
```

## Best Practices

### 1. Always Use Dependency Injection
```python
# Good
agent = InventoryAgent(inventory_service=service)

# Bad
agent = InventoryAgent()  # Creates service internally
```

### 2. Handle Dates Consistently
```python
# Use ISO format strings for input
request_date = "2025-01-15T10:00:00"

# Convert to datetime objects internally
if isinstance(request_date, str):
    request_date = datetime.fromisoformat(request_date)
```

### 3. Return Structured Data
```python
# Good
return {
    "item_name": "A4 paper",
    "available": True,
    "success": True
}

# Bad
return "A4 paper is available"
```

### 4. Use Type Hints
```python
def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
    # Implementation
```

## Extension Points

### Adding New Agents

1. Create new agent class extending `BaseAgent`
2. Implement `process()` method
3. Create system prompts in `prompts/`
4. Register tools in `_register_tools()`
5. Add to factory function in `base.py`
6. Export in `__init__.py`

### Adding New Tools

1. Define tool function within agent's `_register_tools()` method
2. Use `@self._agent.tool` decorator
3. Provide clear docstring with Args and Returns
4. Integrate with service layer methods

## Performance Considerations

- **Caching**: Consider caching frequently accessed inventory data
- **Async Operations**: Future enhancement for concurrent agent calls
- **Rate Limiting**: Monitor LLM API usage and implement rate limiting
- **Logging**: Structured logs enable performance monitoring

## Security Considerations

- **Input Validation**: All inputs validated via Pydantic models
- **Error Messages**: Don't expose sensitive data in error messages
- **API Keys**: Use environment variables, never hardcode
- **Access Control**: Implement in API layer, not agent layer

## Troubleshooting

### Agent Not Responding
- Check `OPENAI_API_KEY` is set
- Verify model name is correct
- Check logs for exceptions

### Tool Not Being Called
- Verify tool registration in `_register_tools()`
- Check tool docstring is clear
- Ensure tool signature matches expectations

### Incorrect Results
- Review system prompts
- Check service layer implementation
- Verify data in database

## References

- [pydantic-ai Documentation](https://github.com/pydantic/pydantic-ai)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [structlog Documentation](https://www.structlog.org/)
- [Implementation Plan](../../../IMPLEMENTATION_PLAN.md)
- [Getting Started Guide](../../../dev/GETTING_STARTED.md)

## Changelog

### v1.0.0 (2025-01-15)
- ✅ Initial implementation of all agents
- ✅ Base agent infrastructure
- ✅ System prompts for all agents
- ✅ Tool registration
- ✅ Service integration
- ✅ Error handling and logging
- ✅ Type safety and validation

