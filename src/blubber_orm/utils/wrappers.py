class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

    def __repr__(self):
        return f"<class Node {self.key}: {self.value}>"

class LinkedList:

    def __init__(self):
        self.head = None

    # @ param: 'key' -> unique identifier of the value
    # @ return: the value held at the key or None if key is not held
    def get(self, key):
        current_node = self.head
        if current_node:
            while current_node.key != key:
                current_node = current_node.next
                if current_node is None:
                    return None
                elif current_node.key == key:
                    break
            return current_node.value
        return None

    # @ param: 'key' -> unique identifier of the value
    # @ param: 'value' -> value to be held at the given key
    def put(self, key, value):
        node = Node(key, value)
        current_node = self.head
        while current_node:
            if current_node.next is None:
                current_node.next = node
                return None
            current_node = current_node.next
        self.head = node

    # @ param: 'key' -> unique identifier of the value
    def delete(self, key):
        current_node = self.head
        if current_node:
            while current_node.key != key:
                next_node = current_node.next
                if next_node is None:
                    return None
                elif next_node.key == key:
                    current_node.next = next_node.next
                else:
                    current_node = next_node
            next_node = self.head.next
            self.head = next_node
        return None

    def length(self):
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next
        return count

    def __repr__(self):
        return f"<class LinkedList: length={self.length()}>"
