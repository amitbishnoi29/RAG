# Python Programming Guide

## Introduction to Python

Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum and first released in 1991, Python has become one of the most popular programming languages in the world.

## Why Python?

### Advantages
- **Easy to Learn**: Simple and readable syntax
- **Versatile**: Used in web development, data science, AI, automation, and more
- **Large Community**: Extensive documentation and community support
- **Rich Libraries**: Vast ecosystem of third-party packages
- **Cross-platform**: Runs on Windows, macOS, and Linux

### Popular Use Cases
- Web development (Django, Flask)
- Data science and analytics (pandas, NumPy, SciPy)
- Machine learning and AI (scikit-learn, TensorFlow, PyTorch)
- Automation and scripting
- Desktop applications
- Game development

## Python Basics

### Variables and Data Types

```python
# Numbers
age = 25
height = 5.9
complex_num = 3 + 4j

# Strings
name = "Alice"
message = 'Hello, World!'
multiline = """This is a
multiline string"""

# Booleans
is_student = True
is_working = False

# Lists
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]

# Dictionaries
person = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# Tuples (immutable)
coordinates = (10, 20)
```

### Control Structures

```python
# If statements
age = 18
if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")

# For loops
for fruit in fruits:
    print(fruit)

for i in range(5):
    print(i)

# While loops
count = 0
while count < 5:
    print(count)
    count += 1
```

### Functions

```python
def greet(name, greeting="Hello"):
    """Function to greet someone"""
    return f"{greeting}, {name}!"

# Function call
message = greet("Alice")
print(message)  # Output: Hello, Alice!

# Lambda functions
square = lambda x: x ** 2
print(square(5))  # Output: 25
```

## Object-Oriented Programming

### Classes and Objects

```python
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer = 0
    
    def drive(self, miles):
        """Simulate driving the car"""
        self.odometer += miles
        print(f"Drove {miles} miles")
    
    def get_info(self):
        """Return car information"""
        return f"{self.year} {self.make} {self.model}"

# Create an object
my_car = Car("Toyota", "Camry", 2020)
print(my_car.get_info())
my_car.drive(100)
```

### Inheritance

```python
class ElectricCar(Car):
    def __init__(self, make, model, year, battery_size):
        super().__init__(make, model, year)
        self.battery_size = battery_size
        self.battery_level = 100
    
    def charge(self):
        """Charge the battery"""
        self.battery_level = 100
        print("Battery fully charged!")
    
    def drive(self, miles):
        """Override parent method"""
        super().drive(miles)
        self.battery_level -= miles * 0.1
        print(f"Battery level: {self.battery_level}%")

tesla = ElectricCar("Tesla", "Model 3", 2021, 75)
tesla.drive(50)
```

## Essential Libraries

### Data Manipulation with pandas

```python
import pandas as pd

# Create a DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'London', 'Tokyo']
}
df = pd.DataFrame(data)

# Basic operations
print(df.head())
print(df.describe())
print(df[df['Age'] > 25])
```

### Numerical Computing with NumPy

```python
import numpy as np

# Create arrays
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# Mathematical operations
print(np.mean(arr))
print(np.sum(matrix, axis=0))
print(np.dot(matrix, matrix))
```

### Data Visualization with Matplotlib

```python
import matplotlib.pyplot as plt

# Simple plot
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.plot(x, y)
plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Simple Line Plot')
plt.show()
```

## Best Practices

### Code Style (PEP 8)
- Use 4 spaces for indentation
- Keep lines under 79 characters
- Use descriptive variable names
- Add docstrings to functions and classes
- Follow naming conventions (snake_case for variables, PascalCase for classes)

### Error Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("This always executes")
```

### Virtual Environments

```bash
# Create virtual environment
python -m venv myenv

# Activate (Windows)
myenv\Scripts\activate

# Activate (macOS/Linux)
source myenv/bin/activate

# Install packages
pip install requests pandas

# Save dependencies
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

## Advanced Topics

### Decorators

```python
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    import time
    time.sleep(1)
    return "Done!"
```

### Context Managers

```python
# File handling with context manager
with open('file.txt', 'r') as f:
    content = f.read()
    # File automatically closed

# Custom context manager
class DatabaseConnection:
    def __enter__(self):
        print("Connecting to database")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing database connection")

with DatabaseConnection() as db:
    print("Using database")
```

### Generators

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Use generator
for num in fibonacci(10):
    print(num)
```

## Testing

### Unit Testing with unittest

```python
import unittest

def add(a, b):
    return a + b

class TestMathFunctions(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
    
    def test_add_strings(self):
        self.assertEqual(add("hello", "world"), "helloworld")

if __name__ == '__main__':
    unittest.main()
```

## Common Patterns

### List Comprehensions

```python
# Basic list comprehension
squares = [x**2 for x in range(10)]

# With condition
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Dictionary comprehension
word_lengths = {word: len(word) for word in ["hello", "world", "python"]}
```

### Working with APIs

```python
import requests

# GET request
response = requests.get('https://api.github.com/users/octocat')
data = response.json()
print(data['name'])

# POST request
payload = {'key': 'value'}
response = requests.post('https://httpbin.org/post', json=payload)
```

## Conclusion

Python's simplicity, versatility, and powerful ecosystem make it an excellent choice for beginners and experienced developers alike. Whether you're building web applications, analyzing data, or developing AI systems, Python provides the tools and libraries you need to succeed. The key to mastering Python is practice and continuous learning from the vibrant Python community.
