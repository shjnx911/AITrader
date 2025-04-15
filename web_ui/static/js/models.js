// Models JavaScript for FreqAI LightGBM model management

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeModelsPage();
    
    // Set up event listeners
    setupEventListeners();
});

// Initialize models page
function initializeModelsPage() {
    // Fetch models
    fetchModels();
    
    // Fetch training configurations
    fetchTrainingConfigs();
}

// Set up event listeners
function setupEventListeners() {
    // Add event listener for new model form
    const newModelForm = document.getElementById('newModelForm');
    if (newModelForm) {
        newModelForm.addEventListener('submit', handleNewModelSubmit);
    }
    
    // Add event listener for new config form
    const newConfigForm = document.getElementById('newConfigForm');
    if (newConfigForm) {
        newConfigForm.addEventListener('submit', handleNewConfigSubmit);
    }
    
    // Add event listener for model filter
    const modelFilter = document.getElementById('modelFilter');
    if (modelFilter) {
        modelFilter.addEventListener('input', filterModels);
    }
}

// Fetch models
function fetchModels() {
    fetch('/api/models')
        .then(response => response.json())
        .then(models => {
            updateModelsTable(models);
        })
        .catch(error => {
            console.error('Error fetching models:', error);
            showAlert('danger', 'Failed to fetch models: ' + error.message);
        });
}

// Update models table
function updateModelsTable(models) {
    const tableBody = document.getElementById('modelsTableBody');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (models.length === 0) {
        // Display no models message
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center">No models available</td>
            </tr>
        `;
        return;
    }
    
    // Add model rows
    models.forEach(model => {
        const row = document.createElement('tr');
        row.setAttribute('data-model-id', model.id);
        row.setAttribute('data-model-name', model.model_name);
        row.setAttribute('data-model-pair', model.pair);
        
        const activeBadge = model.is_active 
            ? '<span class="badge bg-success">Active</span>' 
            : '<span class="badge bg-secondary">Inactive</span>';
            
        const gpuBadge = model.uses_gpu 
            ? '<span class="badge bg-info">GPU</span>' 
            : '<span class="badge bg-light text-dark">CPU</span>';
            
        row.innerHTML = `
            <td>${model.model_name}</td>
            <td>${model.pair}</td>
            <td>${model.timeframe}</td>
            <td>${model.created_date}</td>
            <td>${activeBadge} ${gpuBadge}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-primary view-model" data-bs-toggle="modal" data-bs-target="#modelDetailsModal">View</button>
                    <button type="button" class="btn btn-outline-success activate-model" ${model.is_active ? 'disabled' : ''}>Activate</button>
                    <button type="button" class="btn btn-outline-danger delete-model" ${model.is_active ? 'disabled' : ''}>Delete</button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners for model actions
    addModelActionListeners();
}

// Add event listeners for model actions
function addModelActionListeners() {
    // View model details
    document.querySelectorAll('.view-model').forEach(button => {
        button.addEventListener('click', function() {
            const modelId = this.closest('tr').getAttribute('data-model-id');
            viewModelDetails(modelId);
        });
    });
    
    // Activate model
    document.querySelectorAll('.activate-model').forEach(button => {
        button.addEventListener('click', function() {
            const modelId = this.closest('tr').getAttribute('data-model-id');
            const modelName = this.closest('tr').getAttribute('data-model-name');
            activateModel(modelId, modelName);
        });
    });
    
    // Delete model
    document.querySelectorAll('.delete-model').forEach(button => {
        button.addEventListener('click', function() {
            const modelId = this.closest('tr').getAttribute('data-model-id');
            const modelName = this.closest('tr').getAttribute('data-model-name');
            deleteModel(modelId, modelName);
        });
    });
}

// View model details
function viewModelDetails(modelId) {
    fetch(`/api/models/${modelId}`)
        .then(response => response.json())
        .then(model => {
            // Update modal with model details
            document.getElementById('modelDetailTitle').textContent = model.model_name;
            
            // Update model details
            const detailsContainer = document.getElementById('modelDetailContent');
            if (detailsContainer) {
                let metricsHtml = '';
                if (model.metrics) {
                    metricsHtml = `
                        <div class="card mb-3">
                            <div class="card-header">Model Metrics</div>
                            <div class="card-body">
                                <table class="table table-sm">
                                    <tbody>
                                        ${Object.entries(model.metrics).map(([key, value]) => `
                                            <tr>
                                                <td class="text-capitalize">${key.replace('_', ' ')}</td>
                                                <td>${typeof value === 'number' ? value.toFixed(4) : value}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                }
                
                detailsContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table">
                                <tbody>
                                    <tr>
                                        <th>Trading Pair</th>
                                        <td>${model.pair}</td>
                                    </tr>
                                    <tr>
                                        <th>Timeframe</th>
                                        <td>${model.timeframe}</td>
                                    </tr>
                                    <tr>
                                        <th>Created Date</th>
                                        <td>${model.created_date}</td>
                                    </tr>
                                    <tr>
                                        <th>Status</th>
                                        <td>${model.is_active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}</td>
                                    </tr>
                                    <tr>
                                        <th>Hardware</th>
                                        <td>${model.uses_gpu ? '<span class="badge bg-info">GPU Accelerated</span>' : '<span class="badge bg-light text-dark">CPU Only</span>'}</td>
                                    </tr>
                                    <tr>
                                        <th>Version</th>
                                        <td>${model.version || 'N/A'}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="col-md-6">
                            ${metricsHtml}
                        </div>
                    </div>
                    <div class="mt-3">
                        <h5>Description</h5>
                        <p>${model.description || 'No description available.'}</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching model details:', error);
            showAlert('danger', 'Failed to fetch model details: ' + error.message);
        });
}

// Activate model
function activateModel(modelId, modelName) {
    if (confirm(`Are you sure you want to activate model "${modelName}"?`)) {
        fetch(`/api/models/${modelId}/activate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showAlert('success', result.message);
                fetchModels(); // Refresh the models table
            } else {
                showAlert('danger', result.message);
            }
        })
        .catch(error => {
            console.error('Error activating model:', error);
            showAlert('danger', 'Failed to activate model: ' + error.message);
        });
    }
}

// Delete model
function deleteModel(modelId, modelName) {
    if (confirm(`Are you sure you want to delete model "${modelName}"? This action cannot be undone.`)) {
        fetch(`/api/models/${modelId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showAlert('success', result.message);
                fetchModels(); // Refresh the models table
            } else {
                showAlert('danger', result.message);
            }
        })
        .catch(error => {
            console.error('Error deleting model:', error);
            showAlert('danger', 'Failed to delete model: ' + error.message);
        });
    }
}

// Fetch training configurations
function fetchTrainingConfigs() {
    fetch('/api/configs')
        .then(response => response.json())
        .then(configs => {
            updateConfigsTable(configs);
            populateConfigDropdown(configs);
        })
        .catch(error => {
            console.error('Error fetching training configurations:', error);
            showAlert('danger', 'Failed to fetch training configurations: ' + error.message);
        });
}

// Update configurations table
function updateConfigsTable(configs) {
    const tableBody = document.getElementById('configsTableBody');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    if (configs.length === 0) {
        // Display no configs message
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">No training configurations available</td>
            </tr>
        `;
        return;
    }
    
    // Add config rows
    configs.forEach(config => {
        const row = document.createElement('tr');
        row.setAttribute('data-config-id', config.id);
        row.setAttribute('data-config-name', config.config_name);
        
        const defaultBadge = config.is_default 
            ? '<span class="badge bg-success">Default</span>' 
            : '';
            
        row.innerHTML = `
            <td>${config.config_name} ${defaultBadge}</td>
            <td>${config.created_date}</td>
            <td>${config.description || 'No description'}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-primary view-config" data-bs-toggle="modal" data-bs-target="#configDetailsModal">View</button>
                    <button type="button" class="btn btn-outline-success set-default-config" ${config.is_default ? 'disabled' : ''}>Set Default</button>
                    <button type="button" class="btn btn-outline-danger delete-config">Delete</button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Add event listeners for config actions
    addConfigActionListeners();
}

// Populate config dropdown for model training
function populateConfigDropdown(configs) {
    const configSelect = document.getElementById('trainingConfig');
    if (!configSelect) return;
    
    // Clear existing options
    configSelect.innerHTML = '';
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select a configuration';
    configSelect.appendChild(defaultOption);
    
    // Add config options
    configs.forEach(config => {
        const option = document.createElement('option');
        option.value = config.id;
        option.textContent = config.config_name;
        if (config.is_default) {
            option.selected = true;
        }
        configSelect.appendChild(option);
    });
}

// Add event listeners for config actions
function addConfigActionListeners() {
    // View config details
    document.querySelectorAll('.view-config').forEach(button => {
        button.addEventListener('click', function() {
            const configId = this.closest('tr').getAttribute('data-config-id');
            viewConfigDetails(configId);
        });
    });
    
    // Set default config
    document.querySelectorAll('.set-default-config').forEach(button => {
        button.addEventListener('click', function() {
            const configId = this.closest('tr').getAttribute('data-config-id');
            const configName = this.closest('tr').getAttribute('data-config-name');
            setDefaultConfig(configId, configName);
        });
    });
    
    // Delete config
    document.querySelectorAll('.delete-config').forEach(button => {
        button.addEventListener('click', function() {
            const configId = this.closest('tr').getAttribute('data-config-id');
            const configName = this.closest('tr').getAttribute('data-config-name');
            deleteConfig(configId, configName);
        });
    });
}

// View config details
function viewConfigDetails(configId) {
    fetch(`/api/configs/${configId}`)
        .then(response => response.json())
        .then(config => {
            // Update modal with config details
            document.getElementById('configDetailTitle').textContent = config.config_name;
            
            // Format parameters as JSON
            const paramsJson = JSON.stringify(config.params, null, 2);
            
            // Update config details
            const detailsContainer = document.getElementById('configDetailContent');
            if (detailsContainer) {
                detailsContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-12">
                            <table class="table">
                                <tbody>
                                    <tr>
                                        <th>Created Date</th>
                                        <td>${config.created_date}</td>
                                    </tr>
                                    <tr>
                                        <th>Status</th>
                                        <td>${config.is_default ? '<span class="badge bg-success">Default</span>' : '<span class="badge bg-secondary">Not Default</span>'}</td>
                                    </tr>
                                    <tr>
                                        <th>Description</th>
                                        <td>${config.description || 'No description available.'}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="mt-3">
                        <h5>Parameters</h5>
                        <pre class="bg-dark text-light p-3 rounded"><code>${paramsJson}</code></pre>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching config details:', error);
            showAlert('danger', 'Failed to fetch config details: ' + error.message);
        });
}

// Set default config
function setDefaultConfig(configId, configName) {
    if (confirm(`Are you sure you want to set "${configName}" as the default configuration?`)) {
        fetch(`/api/configs/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                is_default: true
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showAlert('success', `Configuration "${configName}" set as default`);
                fetchTrainingConfigs(); // Refresh the configs table and dropdown
            } else {
                showAlert('danger', result.message);
            }
        })
        .catch(error => {
            console.error('Error setting default config:', error);
            showAlert('danger', 'Failed to set default config: ' + error.message);
        });
    }
}

// Delete config
function deleteConfig(configId, configName) {
    // This would need a backend endpoint
    showAlert('warning', 'Configuration deletion not implemented yet.');
}

// Handle new model submit
function handleNewModelSubmit(event) {
    event.preventDefault();
    
    // Get form data
    const modelName = document.getElementById('modelName').value;
    const tradingPair = document.getElementById('tradingPair').value;
    const timeframe = document.getElementById('timeframe').value;
    const configId = document.getElementById('trainingConfig').value;
    const description = document.getElementById('modelDescription').value;
    
    // Validate form
    if (!modelName || !tradingPair || !timeframe || !configId) {
        showAlert('danger', 'Please fill out all required fields');
        return;
    }
    
    // Show training indicator
    document.getElementById('trainingIndicator').classList.remove('d-none');
    document.getElementById('submitTraining').disabled = true;
    
    // Call API to train model
    fetch('/api/train_model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model_name: modelName,
            pair: tradingPair,
            timeframe: timeframe,
            config_id: configId,
            description: description
        })
    })
    .then(response => response.json())
    .then(result => {
        // Hide training indicator
        document.getElementById('trainingIndicator').classList.add('d-none');
        document.getElementById('submitTraining').disabled = false;
        
        if (result.success) {
            showAlert('success', 'Model training started successfully');
            // Reset form
            document.getElementById('newModelForm').reset();
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newModelModal'));
            if (modal) {
                modal.hide();
            }
            // Refresh models
            fetchModels();
        } else {
            showAlert('danger', result.message);
        }
    })
    .catch(error => {
        // Hide training indicator
        document.getElementById('trainingIndicator').classList.add('d-none');
        document.getElementById('submitTraining').disabled = false;
        
        console.error('Error training model:', error);
        showAlert('danger', 'Failed to train model: ' + error.message);
    });
}

// Handle new config submit
function handleNewConfigSubmit(event) {
    event.preventDefault();
    
    // Get form data
    const configName = document.getElementById('configName').value;
    const configParams = document.getElementById('configParams').value;
    const configDescription = document.getElementById('configDescription').value;
    const isDefault = document.getElementById('isDefaultConfig').checked;
    
    // Validate form
    if (!configName || !configParams) {
        showAlert('danger', 'Please fill out all required fields');
        return;
    }
    
    // Parse JSON parameters
    let parsedParams;
    try {
        parsedParams = JSON.parse(configParams);
    } catch (e) {
        showAlert('danger', 'Invalid JSON in parameters field');
        return;
    }
    
    // Call API to add config
    fetch('/api/configs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            config_name: configName,
            params: parsedParams,
            description: configDescription,
            is_default: isDefault
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('success', 'Configuration added successfully');
            // Reset form
            document.getElementById('newConfigForm').reset();
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newConfigModal'));
            if (modal) {
                modal.hide();
            }
            // Refresh configs
            fetchTrainingConfigs();
        } else {
            showAlert('danger', result.message);
        }
    })
    .catch(error => {
        console.error('Error adding configuration:', error);
        showAlert('danger', 'Failed to add configuration: ' + error.message);
    });
}

// Filter models
function filterModels() {
    const filterText = document.getElementById('modelFilter').value.toLowerCase();
    const rows = document.querySelectorAll('#modelsTableBody tr');
    
    rows.forEach(row => {
        const modelName = row.querySelector('td:first-child').textContent.toLowerCase();
        const pair = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        
        if (modelName.includes(filterText) || pair.includes(filterText)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Show alert
function showAlert(type, message) {
    const alertsContainer = document.getElementById('alertsContainer');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alertsContainer.removeChild(alert);
        }, 500);
    }, 5000);
}
