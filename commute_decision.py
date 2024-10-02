import itertools


class Sentence():

    def evaluate(self, model):
        """Evaluates the logical sentence."""
        raise Exception("nothing to evaluate")

    def formula(self):
        """Returns string formula representing logical sentence."""
        return ""

    def symbols(self):
        """Returns a set of all symbols in the logical sentence."""
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, s):
        """Parenthesizes an expression if not already parenthesized."""
        def balanced(s):
            """Checks if a string has balanced parentheses."""
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if not len(s) or s.isalpha() or (
            s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])
        ):
            return s
        else:
            return f"({s})"


class Symbol(Sentence):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(("symbol", self.name))

    def __repr__(self):
        return self.name

    def evaluate(self, model):
        try:
            return bool(model[self.name])
        except KeyError:
            raise EvaluationException(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}


class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("not", hash(self.operand)))

    def __repr__(self):
        return f"Not({self.operand})"

    def evaluate(self, model):
        return not self.operand.evaluate(model)

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        return self.operand.symbols()


class And(Sentence):
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(
            ("and", tuple(hash(conjunct) for conjunct in self.conjuncts))
        )

    def __repr__(self):
        conjunctions = ", ".join(
            [str(conjunct) for conjunct in self.conjuncts]
        )
        return f"And({conjunctions})"

    def add(self, conjunct):
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        if len(self.conjuncts) == 1:
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(conjunct.formula())
                           for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])


class Or(Sentence):
    def __init__(self, *disjuncts):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        return hash(
            ("or", tuple(hash(disjunct) for disjunct in self.disjuncts))
        )

    def __repr__(self):
        disjuncts = ", ".join([str(disjunct) for disjunct in self.disjuncts])
        return f"Or({disjuncts})"

    def evaluate(self, model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        if len(self.disjuncts) == 1:
            return self.disjuncts[0].formula()
        return " ∨  ".join([Sentence.parenthesize(disjunct.formula())
                            for disjunct in self.disjuncts])

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])


class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return (isinstance(other, Implication)
                and self.antecedent == other.antecedent
                and self.consequent == other.consequent)

    def __hash__(self):
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"

    def evaluate(self, model):
        return ((not self.antecedent.evaluate(model))
                or self.consequent.evaluate(model))

    def formula(self):
        antecedent = Sentence.parenthesize(self.antecedent.formula())
        consequent = Sentence.parenthesize(self.consequent.formula())
        return f"{antecedent} => {consequent}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())


class Biconditional(Sentence):
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (isinstance(other, Biconditional)
                and self.left == other.left
                and self.right == other.right)

    def __hash__(self):
        return hash(("biconditional", hash(self.left), hash(self.right)))

    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"

    def evaluate(self, model):
        return ((self.left.evaluate(model)
                 and self.right.evaluate(model))
                or (not self.left.evaluate(model)
                    and not self.right.evaluate(model)))

    def formula(self):
        left = Sentence.parenthesize(str(self.left))
        right = Sentence.parenthesize(str(self.right))
        return f"{left} <=> {right}"

    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())


def model_check(knowledge, query):
    """Checks if knowledge base entails query."""

    def check_all(knowledge, query, symbols, model):
        """Checks if knowledge base entails query, given a particular model."""

        # If model has an assignment for each symbol
        if not symbols:

            # If knowledge base is true in model, then query must also be true
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:

            # Choose one of the remaining unused symbols
            remaining = symbols.copy()
            p = remaining.pop()

            # Create a model where the symbol is true
            model_true = model.copy()
            model_true[p] = True

            # Create a model where the symbol is false
            model_false = model.copy()
            model_false[p] = False

            # Ensure entailment holds in both models
            return (check_all(knowledge, query, remaining, model_true) and
                    check_all(knowledge, query, remaining, model_false))

    # Get all symbols in both knowledge and query
    symbols = set.union(knowledge.symbols(), query.symbols())

    # Check that knowledge entails query
    return check_all(knowledge, query, symbols, dict())


# Define the symbols for conditions
Rain = Symbol("Rain")  # It's raining
HeavyTraffic = Symbol("HeavyTraffic")  # Traffic is heavy
EarlyMeeting = Symbol("EarlyMeeting")  # You have early meetings
Strike = Symbol("Strike")  # There's a public transport strike
Appointment = Symbol("Appointment")  # You have a doctor's appointment
RoadConstruction = Symbol("RoadConstruction")  # There's road construction

# Define the symbols for commuting options
WFH = Symbol("WFH")  # Work from Home
Drive = Symbol("Drive")  # Drive to the office
PublicTransport = Symbol("PublicTransport")  # Take public transport

# Initialize the knowledge base
knowledge = And()

# Rule 1: If it's raining or there’s an early meeting, you should work from home.
knowledge.add(
    Implication(
        Or(Rain, EarlyMeeting),
        WFH
    )
)

# Rule 2: If it's not raining and there’s no heavy traffic, you should drive.
knowledge.add(
    Implication(
        And(Not(Rain), Not(HeavyTraffic)),
        Drive
    )
)

# Rule 3: If there’s no strike and it’s not raining, you should take public transport.
knowledge.add(
    Implication(
        And(Not(Strike), Not(Rain)),
        PublicTransport
    )
)

# Rule 4: If you have a doctor's appointment, you should drive.
knowledge.add(
    Implication(
        Appointment,
        Drive
    )
)

# Rule 5: If there is road construction, you should avoid driving.
knowledge.add(
    Implication(
        RoadConstruction,
        Not(Drive)
    )
)

# Function to perform model checking for a given scenario
def check_scenario(scenario_conditions, scenario_name):
    # Create a new knowledge base that includes the conditions
    knowledge_scenario = And(knowledge)
    
    # Set of all condition symbols
    all_conditions = {
        'Rain': Rain,
        'HeavyTraffic': HeavyTraffic,
        'EarlyMeeting': EarlyMeeting,
        'Strike': Strike,
        'Appointment': Appointment,
        'RoadConstruction': RoadConstruction
    }
    
    # Add conditions to the knowledge base
    for condition_name, condition_symbol in all_conditions.items():
        if condition_name in scenario_conditions:
            # If condition is specified in the scenario, add it as is
            if scenario_conditions[condition_name]:
                knowledge_scenario.add(condition_symbol)
            else:
                knowledge_scenario.add(Not(condition_symbol))
        else:
            # If condition is unspecified, explicitly set it to False
            knowledge_scenario.add(Not(condition_symbol))
    
    # Now, check if the knowledge base entails each commuting option
    entails_WFH = model_check(knowledge_scenario, WFH)
    entails_Drive = model_check(knowledge_scenario, Drive)
    entails_PublicTransport = model_check(knowledge_scenario, PublicTransport)
    
    # Print the results
    print(f"{scenario_name} entails WFH:", entails_WFH)
    print(f"{scenario_name} entails Drive:", entails_Drive)
    print(f"{scenario_name} entails PublicTransport:", entails_PublicTransport)
    print()

# Scenario 1: It's raining and there's heavy traffic
scenario1_conditions = {
    'Rain': True,
    'HeavyTraffic': True
}
check_scenario(scenario1_conditions, "Scenario 1")

# Scenario 2: There's a public transport strike, and it's not raining
scenario2_conditions = {
    'Strike': True,
    'Rain': False
}
check_scenario(scenario2_conditions, "Scenario 2")

# Scenario 3: There's no rain, traffic is light, and there's no strike
scenario3_conditions = {
    'Rain': False,
    'HeavyTraffic': False,
    'Strike': False
}
check_scenario(scenario3_conditions, "Scenario 3")

# Scenario 4: There's road construction, and you have a doctor's appointment
scenario4_conditions = {
    'RoadConstruction': True,
    'Appointment': True
}
check_scenario(scenario4_conditions, "Scenario 4")
