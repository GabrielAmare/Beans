class SymbolicArray:
    """Array which calculate only when actively required"""
    FILTER = 'filter'
    KEEP = 'keep'
    MAP = 'map'
    APPLY = 'apply'

    S_MAP = 'separate_map'
    S_FILTER = 'separate_filter'
    S_KEEP = 'separate_keep'
    S_APPLY = 'separate_apply'

    operations: list

    def __init__(self, data):
        self.data = data
        self.operations = []

    def __repr__(self):
        if self.operations:
            return super().__repr__()
        else:
            return repr(self.data)

    def __iter__(self):
        for item in self.data:
            for operation, function in self.operations:
                if operation == SymbolicArray.FILTER:
                    if function(item):
                        break
                elif operation == SymbolicArray.S_FILTER:
                    if function(*item):
                        break
                elif operation == SymbolicArray.KEEP:
                    if not function(item):
                        break
                elif operation == SymbolicArray.S_KEEP:
                    if not function(*item):
                        break
                elif operation == SymbolicArray.MAP:
                    item = function(item)
                elif operation == SymbolicArray.S_MAP:
                    item = function(*item)
                elif operation == SymbolicArray.APPLY:
                    function(item)
                elif operation == SymbolicArray.S_APPLY:
                    function(*item)
                else:
                    raise Exception(f"Invalid operation {repr(operation)} !")
            else:
                yield item

    def __getitem__(self, index):
        for item_index, item in enumerate(self):
            if item_index == index:
                return item

    def _symbolic_operation(self, operation, function):
        """Store the symbolic operation associated with <operation> with the <function> given"""
        self.operations.append((operation, function))
        return self

    def filter(self, function):
        """Filter the items when <function> of them is False"""
        return self._symbolic_operation(SymbolicArray.FILTER, function)

    def keep(self, function):
        """Keep the items when <function> of them is True"""
        return self._symbolic_operation(SymbolicArray.KEEP, function)

    def map(self, function):
        """Turn the items into <function> of them"""
        return self._symbolic_operation(SymbolicArray.MAP, function)

    def apply(self, function):
        """Apply the <function> for each item found (do not change the items)"""
        return self._symbolic_operation(SymbolicArray.APPLY, function)

    def sfilter(self, function):
        """Filter the items when <function> of them is False"""
        return self._symbolic_operation(SymbolicArray.S_FILTER, function)

    def skeep(self, function):
        """Keep the items when <function> of them is True"""
        return self._symbolic_operation(SymbolicArray.S_KEEP, function)

    def smap(self, function):
        """Turn the items into <function> of them"""
        return self._symbolic_operation(SymbolicArray.S_MAP, function)

    def sapply(self, function):
        """Apply the <function> for each item found (do not change the items)"""
        return self._symbolic_operation(SymbolicArray.S_APPLY, function)

    def getattr(self, name):
        """Return the attribute value <name> from each item"""
        return self._symbolic_operation(SymbolicArray.MAP, lambda item: getattr(item, name))

    def checkattr(self, name, value):
        """Return the items only if their <name> attribute value is equal to <value>"""
        return self._symbolic_operation(SymbolicArray.KEEP, lambda item: getattr(item, name) == value)

    def finalize(self):
        """Process the operations and return a new SymbolicArray based on the result list"""
        return SymbolicArray(list(self))

    def first(self):
        """Return the first item"""
        for item in self:
            return item

    def max(self, **cfg):
        """Return the greatest item"""
        return max(self, **cfg)

    def min(self, **cfg):
        """Return the lowest item"""
        return min(self, **cfg)

    def last(self):
        """Return the last item"""
        item = None
        for item in self:
            pass
        return item

    def append(self, item):
        """relayed method to avoid the use of self.data.append"""
        return self.data.append(item)

    def extend(self, items):
        """relayed method to avoid the use of self.data.extend"""
        return self.data.extend(items)

    def remove(self, item):
        """relayed method to avoid the use of self.data.remove"""
        return self.data.remove(item)


if __name__ == '__main__':
    query = SymbolicArray(range(1, 100_000))
    print(query)
    query = query.filter(lambda x: x % 5).map(lambda x: 3 * x - 7)
    print(query)
    result = query.finalize()
    print(result)


    print(SymbolicArray(range(10))
        .map(lambda item: (item-1, item+1))
        .skeep(lambda i, j: (i % 3 == 0) or (j % 3 == 0))
        .smap(lambda i, j: i * j)
        .finalize())