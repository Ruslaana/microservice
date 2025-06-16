class Stack:
    def __init__(self, max_size=2):
        self.stack = []
        self.max_size = max_size

    def push(self, item):
        if len(self.stack) >= self.max_size:
            self.stack.pop(0)
        self.stack.append(item)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def peek(self):
        return self.stack[-1] if self.stack else None

    def is_empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)

    def __repr__(self):
        return f"Stack({self.stack})"
