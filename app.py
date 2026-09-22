"""Sample application module for DevOps practice."""


def add(a: int, b: int) -> int:
    """Return the sum of two numbers."""
    return a + b


def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


def main() -> None:
    """Execute main application logic."""
    message = greet("DevOps")
    print(message)
    result = add(10, 20)
    print(f"10 + 20 = {result}")


if __name__ == "__main__":
    main()
