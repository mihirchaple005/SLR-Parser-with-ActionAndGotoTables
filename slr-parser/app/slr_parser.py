# Gramme class is working fine all first and follow are calculated corrctly

class Grammar:
    def __init__(self, productions):
        self.productions = productions
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = productions[0][0]
        self._process_productions()
        self.first_sets = {}
        self.follow_sets = {}
        self._compute_first_sets()
        self._compute_follow_sets()
        
    def _process_productions(self):
        for head, body in self.productions:
            self.non_terminals.add(head)
            for symbol in body:
                if symbol.isupper() and symbol != 'ε':
                    self.non_terminals.add(symbol)
                else:
                    if symbol != 'ε':
                        self.terminals.add(symbol)
        self.terminals.add('$')  # End marker

    def _compute_first_sets(self):
        # Initialize FIRST sets
        for non_terminal in self.non_terminals:
            self.first_sets[non_terminal] = set()
        for terminal in self.terminals:
            self.first_sets[terminal] = {terminal}

        # Iteratively compute FIRST sets
        changed = True
        while changed:
            changed = False
            for head, body in self.productions:
                # For each production A → α
                for symbol in body:
                    # Add FIRST(symbol) to FIRST(A)
                    before = len(self.first_sets[head])
                    self.first_sets[head].update(self.first_sets.get(symbol, set()))
                    if len(self.first_sets[head]) > before:
                        changed = True
                    if 'ε' not in self.first_sets.get(symbol, set()):
                        break
                else:
                    # All symbols can derive ε, so add ε to FIRST(A)
                    if 'ε' not in self.first_sets[head]:
                        self.first_sets[head].add('ε')
                        changed = True
        # print("First sets: ", self.first_sets)

    def _compute_follow_sets(self):
        # Initialize FOLLOW sets
        for non_terminal in self.non_terminals:
            self.follow_sets[non_terminal] = set()
        self.follow_sets[self.start_symbol].add('$')

        # Iteratively compute FOLLOW sets
        
        changed = True
        while changed:
            changed = False
            for head, body in self.productions:
                # For each production A → αBβ
                for i in range(len(body)):
                    B = body[i]
                    if B not in self.non_terminals:
                        continue
                    
                    # Case 1: A → αBβ, add FIRST(β)-{ε} to FOLLOW(B)
                    β = body[i+1:]
                    if β:
                        first_β = self._first_of_sequence(β)
                        before = len(self.follow_sets[B])
                        self.follow_sets[B].update(first_β - {'ε'})
                        if len(self.follow_sets[B]) > before:
                            changed = True
                    
                    # Case 2: A → αB or A → αBβ where β derives ε, add FOLLOW(A) to FOLLOW(B)
                    if not β or 'ε' in self._first_of_sequence(β):
                        before = len(self.follow_sets[B])
                        self.follow_sets[B].update(self.follow_sets[head])
                        if len(self.follow_sets[B]) > before:
                            changed = True
        print("Follow sets: ", self.follow_sets)

    def _first_of_sequence(self, sequence):
        first = set()
        for symbol in sequence:
            first.update(self.first_sets.get(symbol, set()) - {'ε'})
            if 'ε' not in self.first_sets.get(symbol, set()):
                break
        else:
            first.add('ε')
        return first


class SLRParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.states = []
        self.transitions = {}
        self.action_table = []
        self.goto_table = []
        self.build_parsing_table()

    def closure(self, items : set):
        """
        Compute the closure of a set of LR(0) items
        
        Args:
            items: A set of LR(0) items where each item is a tuple (head, body, position)
                   e.g., ('E', ['E', '+', 'T'], 0)
        
        Returns:
            The closure set of items
        """
        print(items)
        closure_set = list(items)  # Start with the original items
        print("This is closure set", closure_set)
        changed = True
        print("Before while")
        while changed:
            changed = False
            current_items = closure_set  # Make a copy to iterate over
            print("while ke andaer") 
            print("current items : ", current_items)
            for (head, body, pos) in current_items:
                print("inside")
                # If we've reached the end of the production, skip
                print("pos : ", pos)
                if pos >= len(body):
                    
                    continue
                   
                next_symbol = body[pos]
                

                # If next symbol is a non-terminal, add its productions
                if next_symbol in self.grammar.non_terminals:
                    for prod_head, prod_body in self.grammar.productions:
                        if prod_head == next_symbol:
                            new_item = (prod_head, prod_body, 0)
                            if new_item not in closure_set:
                                closure_set.add(new_item)
                                changed = True
        print("This is clousure set",closure_set)                        
        return closure_set

    def goto(self, items, symbol):
        """
        Compute the GOTO set for a set of LR(0) items and a grammar symbol
        
        Args:
            items: A set of LR(0) items (each item is a tuple: (head, body, position))
            symbol: The grammar symbol to transition on (terminal or non-terminal)
        
        Returns:
            The GOTO set (closure of the moved items)
        """
        moved_items = set()
        
        for (head, body, pos) in items:
            # Check if we can move the dot past this symbol
            if pos < len(body) and body[pos] == symbol:
                new_item = (head, body, pos + 1)
                moved_items.add(new_item)
        
        # Return the closure of the moved items
        return self.closure(moved_items) if moved_items else set()

    def build_canonical_collection(self):
        print("Mei canonical collections mei hu")
        """
        Build the canonical collection of LR(0) items for the grammar
        
        Returns:
            A tuple containing:
            - The list of all LR(0) item sets (states)
            - The transition dictionary (GOTO table)
        """
        # Create augmented grammar by adding S' -> S production
        augmented_start = self.grammar.start_symbol + "'"
        initial_item = (augmented_start, [self.grammar.start_symbol], 0)
        print("INITIAL ITEMS", initial_item)
        # Initialize the canonical collection with the closure of the initial item
        start_state = self.closure(initial_item)
        print("nohubhinonibnlnoobhk")
        self.states = [start_state]
        print("This is states of parser")
        self.transitions = {}
        
        changed = True
        while changed:
            changed = False
            
            for i, state in enumerate(self.states):
                # Check all possible symbols that appear after dots in this state
                symbols_after_dots = set()
                for (head, body, pos) in state:
                    if pos < len(body):
                        symbols_after_dots.add(body[pos])
                
                # Compute GOTO for each symbol
                for symbol in symbols_after_dots:
                    new_state = frozenset(self.goto(state, symbol))
                    
                    if not new_state:  # Empty GOTO result
                        continue
                    
                    # Check if this is a new state
                    if new_state not in self.states:
                        self.states.append(new_state)
                        changed = True
                    
                    # Record the transition
                    target_index = self.states.index(new_state)
                    self.transitions[(i, symbol)] = target_index

    def build_parsing_table(self):
        
        """
        Construct the SLR parsing table (ACTION and GOTO tables)
        
        Returns:
            A tuple containing (action_table, goto_table)
        """
        # First build the canonical collection if not already built
        # if not hasattr(self, 'states') or not hasattr(self, 'transitions'):
        print("build parsing table ke andar hu")
        self.build_canonical_collection()
        
        # Initialize tables
        self.action_table = [{} for _ in range(len(self.states))]
        self.goto_table = [{} for _ in range(len(self.states))]
        
        # Build the GOTO table from transitions (for non-terminals)
        for (state_idx, symbol), target_idx in self.transitions.items():
            if symbol in self.grammar.non_terminals:
                self.goto_table[state_idx][symbol] = target_idx
            else:  # Terminal symbols go to ACTION table as shifts
                self.action_table[state_idx][symbol] = ('shift', target_idx)
        print("goto ka karekram", self.goto_table)
        # Add reduce actions based on FOLLOW sets
        for state_idx, state in enumerate(self.states):
            for item in state:
                head, body, pos = item
                
                # If dot is at end (reduce item)
                if pos == len(body):
                    # For augmented production S' -> S•, add accept
                    if head == self.grammar.start_symbol + "'":
                        self.action_table[state_idx]['$'] = ('accept',)
                    else:
                        # For normal productions, add reduce actions
                        for follow_symbol in self.grammar.follow_sets[head]:
                            if follow_symbol in self.action_table[state_idx]:
                                raise ValueError(f"Shift-Reduce conflict at state {state_idx} for symbol {follow_symbol}")
                            self.action_table[state_idx][follow_symbol] = ('reduce', head, body)
        print('this is karekram',self.action_table)
        print("This is andar ka grammar", self.grammar.productions)
        return self.action_table, self.goto_table

    def parse(self, input_string):
        """
        Parse an input string using the SLR parsing tables
        
        Args:
            input_string: The string to parse (space-separated tokens)
        
        Returns:
            A tuple (success, output) where:
            - success: Boolean indicating if parsing succeeded
            - output: List of parsing steps
        """
        input_tokens = input_string.split() + ['$']
        stack = [0]  # Start with initial state
        output = []
        idx = 0
        
        while True:
            state = stack[-1]
            current_token = input_tokens[idx]
            
            if current_token not in self.action_table[state]:
                raise ValueError(f"Syntax error: No action for token {current_token} in state {state}")
            
            action = self.action_table[state][current_token]
            
            if action[0] == 'shift':
                stack.append(current_token)
                stack.append(action[1])
                idx += 1
                output.append(f"Shift {current_token}")
            
            elif action[0] == 'reduce':
                head, body = action[1], action[2]
                for _ in range(2 * len(body)):
                    stack.pop()
                state = stack[-1]
                stack.append(head)
                if head not in self.goto_table[state]:
                    raise ValueError(f"Syntax error: No goto for {head} in state {state}")
                stack.append(self.goto_table[state][head])
                output.append(f"Reduce {head} → {' '.join(body)}")
            
            elif action[0] == 'accept':
                output.append("Accept")
                return True, output
            
            else:
                raise ValueError(f"Unknown action: {action}")