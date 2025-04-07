document.addEventListener('DOMContentLoaded', function () {
    const grammarContainer = document.getElementById('grammar-inputs');
    const addProductionBtn = document.getElementById('add-production');
    const buildTableBtn = document.getElementById('build-table');
    const parseBtn = document.getElementById('parse-btn');

    // Add Production Input
    if (addProductionBtn) {
        addProductionBtn.addEventListener('click', function () {
            const div = document.createElement('div');
            div.className = 'production';
            div.innerHTML = `
                <input type="text" class="production-input" placeholder="E -> E + T">
                <button class="remove-btn">Remove Production</button>
            `;
            grammarContainer.appendChild(div);
            console.log(div);
        });
    }

    // Remove Production Input (Event Delegation)
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-btn')) {
            event.target.parentElement.remove();
            console.log("removed", event.target.parentElement);
            
        }
    });

    // Build Parsing Table
    if (buildTableBtn) {
        buildTableBtn.addEventListener('click', function () {
            const productions = Array.from(document.querySelectorAll('.production-input'))
                .map(input => input.value.trim())
                .filter(value => value !== '');

            if (productions.length === 0) {
                showError('Please add at least one production');
                return;
            }

            for (const prod of productions) {
                if (!prod.includes('->')) {
                    showError(`Invalid production format: "${prod}". Use "A -> B C" format.`);
                    return;
                }
            }

            buildTableBtn.disabled = true;
            buildTableBtn.textContent = 'Building...';

            fetch('/parse_grammar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ productions: productions })
            })
                .then(response => response.ok ? response.json() : Promise.reject(response) && console.log(response))
                .then(data => {
                    if (data.status === 'success') {
                        displayTables(data.action_table, data.goto_table, data.states);
                        showSuccess('Parsing tables built successfully!');
                    } else {
                        throw new Error(data.message || 'Unknown error occurred');
                    }
                })
                .catch(error => showError('Error building tables: ' + (error.message || error)))
                .finally(() => {
                    buildTableBtn.disabled = false;
                    buildTableBtn.textContent = 'Build Parsing Table';
                });
        });
    }

    // Parse Input String
    if (parseBtn) {
        parseBtn.addEventListener('click', function () {
            const inputString = document.getElementById('input-string').value.trim();
            if (inputString === '') {
                showError('Please enter an input string');
                return;
            }

            const productions = Array.from(document.querySelectorAll('.production-input'))
                .map(input => input.value.trim())
                .filter(value => value !== '');

            if (productions.length === 0) {
                showError('Please add grammar productions first');
                return;
            }

            parseBtn.disabled = true;
            parseBtn.textContent = 'Parsing...';

            fetch('/parse_input', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ productions: productions, input_string: inputString })
            })
                .then(response => response.ok ? response.json() : Promise.reject(response))
                .then(data => {
                    if (data.status === 'success') {
                        displayParseResult(data.result);
                        showSuccess('Parsing completed successfully!');
                    } else {
                        throw new Error(data.message || 'Unknown error occurred during parsing');
                    }
                })
                .catch(error => showError('Error parsing input: ' + (error.message || error)))
                .finally(() => {
                    parseBtn.disabled = false;
                    parseBtn.textContent = 'Parse';
                });
        });
    }

    // Display Parsing Tables
    function displayTables(actionTable, gotoTable, states) {
        let actionHtml = '<h3>ACTION Table</h3><table class="parsing-table"><tr><th>State</th>';

        const actionSymbols = new Set();
        actionTable.forEach(stateActions => {
            Object.keys(stateActions).forEach(symbol => actionSymbols.add(symbol));
        });

        Array.from(actionSymbols).sort().forEach(symbol => {
            actionHtml += `<th>${symbol}</th>`;
        });
        actionHtml += '</tr>';

        actionTable.forEach((stateActions, stateIdx) => {
            actionHtml += `<tr><td>${stateIdx}</td>`;
            Array.from(actionSymbols).sort().forEach(symbol => {
                const action = stateActions[symbol] || '';
                let display = '';
                if (Array.isArray(action)) {
                    if (action[0] === 'shift') display = `s${action[1]}`;
                    else if (action[0] === 'reduce') display = `r${action[1]}→${action[2].join(' ')}`;
                    else if (action[0] === 'accept') display = 'acc';
                }
                actionHtml += `<td>${display}</td>`;
            });
            actionHtml += '</tr>';
        });
        actionHtml += '</table>';

        document.getElementById('action-table-container').innerHTML = actionHtml;

        let gotoHtml = '<h3>GOTO Table</h3><table class="parsing-table"><tr><th>State</th>';
        const gotoSymbols = new Set();
        gotoTable.forEach(stateGotos => {
            Object.keys(stateGotos).forEach(symbol => gotoSymbols.add(symbol));
        });

        Array.from(gotoSymbols).sort().forEach(symbol => {
            gotoHtml += `<th>${symbol}</th>`;
        });
        gotoHtml += '</tr>';

        gotoTable.forEach((stateGotos, stateIdx) => {
            gotoHtml += `<tr><td>${stateIdx}</td>`;
            Array.from(gotoSymbols).sort().forEach(symbol => {
                const gotoState = stateGotos[symbol] || '';
                gotoHtml += `<td>${gotoState}</td>`;
            });
            gotoHtml += '</tr>';
        });
        gotoHtml += '</table>';

        document.getElementById('goto-table-container').innerHTML = gotoHtml;
    }

    // Display Parsing Result
    function displayParseResult(result) {
        const resultDiv = document.getElementById('parse-result');
        if (typeof result === 'string') {
            resultDiv.innerHTML = `<div class="success">${result}</div>`;
        } else if (Array.isArray(result)) {
            resultDiv.innerHTML = result.map(step => `<div>${step}</div>`).join('');
        } else {
            resultDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
        }
    }

    // Error Display
    function showError(message) {
        document.getElementById('parse-result').innerHTML = `<div class="error">${message}</div>`;
    }

    // Success Display
    function showSuccess(message) {
        document.getElementById('parse-result').innerHTML = `<div class="success">${message}</div>`;
    }
});

document.getElementById('build-table').addEventListener('click', function() {
    const productions = [];
    document.querySelectorAll('.production-input').forEach(input => {
        if (input.value) {
            console.log(input.value);
            productions.push(input.value);
        }
    });

    fetch('/parse_grammar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ productions })
    })
    .then(response => {
        response.json()
        console.log(response);
        })
    .then(data => {
        console.log(data);
        
        if (data.status === 'success') {
            // Clear existing tables
            document.getElementById('action-table-container').innerHTML = '';
            document.getElementById('goto-table-container').innerHTML = '';

            // Display action table
            const actionTable = data.action_table;
            const actionTableContainer = document.getElementById('action-table-container');
            const actionTableElement = document.createElement('table');
            actionTableElement.classList.add('parsing-table');
            let header = '<thead><tr><th>State</th><th>Action</th></tr></thead><tbody>';
            actionTable.forEach((state, index) => {
                for (const symbol in state) {
                    header += `<tr><td>${index}</td><td>${state[symbol]}</td></tr>`;
                }
            });
            header += '</tbody>';
            actionTableElement.innerHTML = header;
            actionTableContainer.appendChild(actionTableElement);

            // Display goto table
            const gotoTable = data.goto_table;
            const gotoTableContainer = document.getElementById('goto-table-container');
            const gotoTableElement = document.createElement('table');
            gotoTableElement.classList.add('parsing-table');
            header = '<thead><tr><th>State</th><th>Goto</th></tr></thead><tbody>';
            gotoTable.forEach((state, index) => {
                for (const symbol in state) {
                    header += `<tr><td>${index}</td><td>${state[symbol]}</td></tr>`;
                }
            });
            header += '</tbody>';
            gotoTableElement.innerHTML = header;
            gotoTableContainer.appendChild(gotoTableElement);
        } else {
            alert(data.message || 'An error occurred.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to build parsing tables.');
    });
});

