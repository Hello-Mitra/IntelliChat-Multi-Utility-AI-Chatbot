from langchain_core.tools import tool


@tool
def calculator(first_number: float, second_number: float, operation: str) -> dict:
    """
    A simple calculator tool that performs basic arithmetic operations.

    Args:
        first_number: The first number.
        second_number: The second number.
        operation: The operation — add, subtract, multiply, divide.

    Returns:
        A dict containing the result.
    """
    try:
        if operation == "add":
            result = first_number + second_number
        elif operation == "subtract":
            result = first_number - second_number
        elif operation == "multiply":
            result = first_number * second_number
        elif operation == "divide":
            if second_number == 0:
                raise ValueError("Division by zero is not allowed.")
            result = first_number / second_number
        else:
            raise ValueError(
                f"Invalid operation '{operation}'. "
                "Supported: add, subtract, multiply, divide."
            )
        return {
            "first_number": first_number,
            "second_number": second_number,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}
