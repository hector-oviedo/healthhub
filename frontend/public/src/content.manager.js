class ContentGenerator {
    constructor() {
        
    }
    createInput(inputData) {
        const inputGroup = document.createElement('div');
        inputGroup.className = 'mb-3';
        inputGroup.id = inputData.name;
        let input;

        switch (inputData.type) {
            case 'text':
            case 'password':
            case 'email':
                input = document.createElement('input');
                input.type = inputData.type;
                input.className = 'form-control';
                input.name = inputData.name;
                input.placeholder = inputData.placeholder || inputData.label;
                if ('value' in inputData) {
                    input.value = inputData.value;
                }
                inputGroup.appendChild(input);
                break;
            case 'checkbox':
                inputGroup.className = 'form-check mb-3';
    
                input = document.createElement('input');
                input.type = 'checkbox';
                input.className = 'form-check-input';
                input.id = inputData.name; // Unique ID for the checkbox
                input.name = inputData.name;
    
                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = inputData.name;
                label.textContent = inputData.label;
    
                inputGroup.appendChild(input);
                inputGroup.appendChild(label);
                break;
            case 'select':
                input = document.createElement('select');
                input.className = 'form-select';
                input.name = inputData.name;
                input.addEventListener('change', function() {
                    // 'this' refers to the select element
                    let selectedValue = this.value;
                    console.log('Selected value:', selectedValue); // You can handle the selected value here
                    input.value = selectedValue;
                });
                inputData.options.forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option.value;
                    optionElement.textContent = option.label;
                    input.appendChild(optionElement);
                });
                inputGroup.appendChild(input);
                break;
            case 'slider':
                input = document.createElement('input');
                input.type = 'range';
                input.name = inputData.name;
                input.className = 'form-range';
                if ('value' in inputData) input.value = inputData.value;
                inputGroup.appendChild(input);
                break;
            case 'date':
                inputGroup.className = 'mb-3 row';
                inputGroup.id = "date_" + inputData.name;
                
                // Column for the date input and label
                const dateCol = document.createElement('div');
                dateCol.className = 'col-md-6';
                
                const dateLabel = document.createElement('label');
                dateLabel.textContent = inputData.label;
                dateLabel.style.textAlign = 'left';
                dateLabel.style.width = '100%';
                dateLabel.htmlFor = inputData.name + '_date'; // Set the 'for' attribute for the date input
                
                // Create the date input
                const dateInput = document.createElement('input');
                dateInput.type = 'date';
                dateInput.className = 'form-control';
                dateInput.id = inputData.placeholder+inputData.name + '_date'; // Set the 'id' for the date input
                dateInput.name = inputData.placeholder+inputData.name + '_date';
                
                // Append the date label and input to the date column
                dateCol.appendChild(dateLabel);
                dateCol.appendChild(dateInput);
                
                // Column for the time input and label
                const timeCol = document.createElement('div');
                timeCol.className = 'col-md-6';
                
                const timeLabel = document.createElement('label');
                timeLabel.textContent = '';
                timeLabel.style.textAlign = 'left';
                timeLabel.htmlFor = inputData.name + '_time'; // Set the 'for' attribute for the time input
                
                // Create the time input
                const timeInput = document.createElement('input');
                timeInput.type = 'time';
                timeInput.className = 'form-control';
                timeInput.id = inputData.placeholder+inputData.name + '_time'; // Set the 'id' for the time input
                timeInput.name = inputData.placeholder+inputData.name + '_time';
                
                // Append the time label and input to the time column
                timeCol.appendChild(timeLabel);
                timeCol.appendChild(timeInput);
                
                // Append the date and time columns to the row
                inputGroup.appendChild(dateCol);
                inputGroup.appendChild(timeCol);

                inputGroup.dateElement = dateInput;
                inputGroup.timeElement = timeInput;
                break;
                
            case 'hidden': // Add support for hidden input type
                input = document.createElement('input');
                input.type = 'hidden';
                input.name = inputData.name;
                input.value = inputData.value;
                inputGroup.appendChild(input);
                break;
                default:
                console.error('Unsupported input type:', inputData.type);
                return null;
        }
        return inputGroup;
    }

    // Method to generate a table
    generateTable(tableData) {
        // Create a container for the table with fixed height and scroll
        const tableContainer = document.createElement('div');
        tableContainer.className = 'table-scrollable-container custom-table-scrollable';
    
        // Create the table
        const table = document.createElement('table');
        table.className = 'table';
    
        // Create the header
        const thead = document.createElement('thead');
        thead.style.position = 'sticky';
        thead.style.top = '0';
        const headerRow = document.createElement('tr');
        tableData.headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            th.style.backgroundColor = "#202123";
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
    
        // Create the body
        const tbody = document.createElement('tbody');
        tableData.rows.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.style.textAlign = cell.align || "center";
                if (cell.type === 'action') {
                    const removeButton = document.createElement('button');
                    removeButton.textContent = cell.label || "Action";
                    removeButton.className = cell.btnStyle || 'btn btn-outline-danger';
                    removeButton.onclick = () => cell.action(cell.value);
                    td.appendChild(removeButton);
                } else td.textContent = cell.value;
                
                tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    // Append the table to the container
    tableContainer.appendChild(table);

    return tableContainer;
}
    

    // Method to generate a form with text inputs
    async generateForm(formData) {
        let form = document.createElement('form');
        formData.inputs.forEach(inputData => {
            let input = this.createInput(inputData);
            if (input) form.appendChild(input);
        });

        let submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.className = formData.buttonStyle || 'btn btn-outline-light';
        submitButton.textContent = formData.buttonLabel || 'Submit';
        
        let buttonContainer = document.createElement('div');
        buttonContainer.style.width = '100%';
        buttonContainer.style.textAlign = formData.buttonAlign || 'left';
        buttonContainer.appendChild(submitButton);

        form.appendChild(buttonContainer);

        // Handle form submission
        form.onsubmit = (e) => {
            e.preventDefault();
            let formDataJSON = {};
            formData.inputs.forEach(inputData => {
                if (inputData.type == 'date') {
                    const dateEl = document.getElementById(inputData.placeholder+inputData.name +'_date');
                    const timeEl = document.getElementById(inputData.placeholder+inputData.name +'_time');
                    const dateValue = dateEl.value;
                    const timeValue = timeEl.value;
                    if (dateValue && timeValue) formDataJSON[inputData.name] = formatDateToService(dateValue, timeValue);
                } else formDataJSON[inputData.name] = form.elements[inputData.name].value;
            });
            

            backendService.sendRequest(formData.action, 'POST', formDataJSON)
                .then(response => {
                    if (formData.onSuccess && typeof formData.onSuccess === 'function') {
                        formData.onSuccess(response);
                    }
                })
                .catch(error => formData.onSuccess({success:false, error:error}));
        };

        return form;
    }

    // render an individual item
    async renderItem(item, container) {
        switch (item.type) {
            case 'title':
                let title = document.createElement('h2');
                title.textContent = item.text;
                title.style.textAlign = item.align || 'center';
                container.appendChild(title);
                break;
            case 'parragraph':
                let paragraph = document.createElement('p');
                paragraph.innerHTML = item.text;
                paragraph.style.textAlign = item.align || 'center';
                container.appendChild(paragraph);
                break;
            case 'div':
                let div = document.createElement('div');
                div = item.innerHTML;
                div.style.textAlign = item.align || 'center';
                container.appendChild(div);
                break;
            case 'separator':
                let separator = document.createElement('hr');
                container.appendChild(separator);
                break;
            case 'table':
                container.appendChild(this.generateTable(item));
                break;
            case 'form':
                const form = await this.generateForm(item);
                container.appendChild(form);
                break;
            // Additional cases as needed
        }
    }

    // render content based on JSON data
    async renderContent(elementOrId, jsonData) {
        const container = (typeof elementOrId === 'string') ? document.getElementById(elementOrId) : elementOrId;
        if (!container) {
            console.error('Invalid element/element ID provided (ContentGenerator)');
            return;
        }
    
        for (let item of jsonData) {
            await this.renderItem(item, container);
        }
    }

    // render content in multiple columns
    async renderMultiColContent(elementOrId, columnsData) {
        let container = (typeof elementOrId === 'string') ? document.getElementById(elementOrId) : elementOrId;
        if (!container) {
            console.error('Invalid element/element ID provided (ContentGenerator)');
            return;
        }
        
        let row = document.createElement('div');
        row.className = 'row'; // Bootstrap row class

        for (let colData of columnsData) {
            let col = document.createElement('div');
            col.className = `col-${colData.cols}`; // Bootstrap column class

            for (let item of colData.content) {
                await this.renderItem(item, col);
            }

            row.appendChild(col);
        }

        container.appendChild(row);
    }
}