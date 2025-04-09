from flask import Blueprint, render_template, request, jsonify
from app.slr_parser import Grammar, SLRParser
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

bp = Blueprint('main', __name__)
CORS(bp)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/parse_grammar', methods=['POST'])
def parse_grammar():
    data = request.get_json()
    if not data or 'productions' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request format. Expected JSON with productions.'
        }), 400

    productions = []
    
    try:
        # Check and format the productions
        for prod in data['productions']:
            if '->' not in prod:
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid production format: "{prod}". Use "A -> B C" format.'
                }), 400
            
            head, body = prod.split('->', 1)
            productions.append((head.strip(), body.strip().split()))
        # Initialize the Grammar and SLR Parser
        grammar = Grammar(productions)
        parser = SLRParser(grammar)

        # Convert parsing tables to serializable format
        action_table = []
        for state_actions in parser.action_table:
            serialized = {}
            for symbol, action in state_actions.items():
                if isinstance(action, tuple):
                    serialized[symbol] = list(action)  # Convert tuple to list
                else:
                    serialized[symbol] = action
            action_table.append(serialized)
        goto_table = []
        for state_gotos in parser.goto_table:
            serialized = {}
            for symbol, goto_state in state_gotos.items():
                serialized[symbol] = goto_state
            goto_table.append(serialized)

        # Convert states to serializable format
        states = []
        for state in parser.states:
            serialized_state = []
            for item in list(state):
                head, body, pos = item
                serialized_state.append([head, body, pos])
            states.append(serialized_state)
        print(action_table)
        print(goto_table)
        return jsonify({
            'status': 'success',
            'action_table': action_table,
            'goto_table': goto_table,
            'states': states
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # 🔍 See full error in terminal
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route('/parse_input', methods=['POST'])
def parse_input():
    data = request.get_json()
    if not data or 'input_string' not in data or 'productions' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request format. Expected JSON with input_string and productions.'
        }), 400

    print("Data ",data)
    print(type(data))
    input_string = data['input_string']
    print(input_string)
    print(type(input_string))

    try:
        # Parse the grammar productions
        productions = []
        for prod in data['productions']:
            if '->' not in prod:
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid production format: "{prod}". Use "A -> B C" format.'
                }), 400
            
            head, body = prod.split('->', 1)
            productions.append((head.strip(), body.strip().split()))

        # Initialize the Grammar and SLR Parser
        grammar = Grammar(productions)
        parser = SLRParser(grammar)

        # Parse the input string
        print("halelulu",type(input_string))
        success, steps = parser.parse(input_string.split())

        if success:
            return jsonify({
                'status': 'success',
                'result': steps
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Parsing failed.'
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
