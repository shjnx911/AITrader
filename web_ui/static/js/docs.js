/**
 * Documentation system for AITradeStrategist
 * Manages the display of documentation content
 */

// Documentation content categories
const docCategories = {
    'getting-started': {
        title: 'Getting Started',
        icon: 'bi-play-circle',
        order: 1
    },
    'dashboard': {
        title: 'Dashboard',
        icon: 'bi-speedometer2',
        order: 2
    },
    'performance': {
        title: 'Performance Analysis',
        icon: 'bi-graph-up',
        order: 3
    },
    'models': {
        title: 'Model Management',
        icon: 'bi-braces',
        order: 4
    },
    'settings': {
        title: 'Settings',
        icon: 'bi-gear',
        order: 5
    },
    'strategies': {
        title: 'Trading Strategies',
        icon: 'bi-lightning',
        order: 6
    },
    'freqtrade': {
        title: 'Freqtrade Integration',
        icon: 'bi-hdd-network',
        order: 7
    },
    'api': {
        title: 'API Documentation',
        icon: 'bi-code-slash',
        order: 8
    },
    'faq': {
        title: 'FAQ',
        icon: 'bi-question-circle',
        order: 9
    }
};

// Documentation content
const docContent = {
    // Getting Started
    'getting-started-introduction': {
        category: 'getting-started',
        title: 'Introduction',
        content: `
<h2>Welcome to AITradeStrategist</h2>
<p>AITradeStrategist is an advanced cryptocurrency trading platform that combines the power of AI/ML with Freqtrade's robust trading capabilities. This integrated solution allows you to develop, test, and deploy sophisticated trading strategies powered by machine learning models.</p>

<h3>Key Features</h3>
<ul>
    <li><strong>AI-Powered Trading:</strong> Utilize LightGBM machine learning models to analyze market data and make prediction-based trading decisions.</li>
    <li><strong>GPU Acceleration:</strong> Optimize model training performance with AMD GPU support through DirectML.</li>
    <li><strong>Comprehensive Dashboard:</strong> Monitor your trading performance with intuitive visualizations and detailed metrics.</li>
    <li><strong>Model Management:</strong> Create, test, deploy, and monitor multiple trading models across different cryptocurrencies and timeframes.</li>
    <li><strong>Strategy Recommendations:</strong> Receive AI-generated strategy suggestions based on market conditions and your risk preferences.</li>
    <li><strong>Performance Analysis:</strong> Conduct in-depth analysis of your trading performance with detailed metrics and charts.</li>
    <li><strong>Freqtrade Integration:</strong> Seamlessly connect with Freqtrade for actual trading execution.</li>
</ul>

<h3>System Requirements</h3>
<ul>
    <li><strong>Recommended:</strong> AMD GPU with at least 8GB VRAM for accelerated model training</li>
    <li><strong>Alternative:</strong> CPU-only mode (slower model training but fully functional)</li>
    <li>Modern web browser with JavaScript enabled</li>
    <li>Freqtrade instance (for live trading functionality)</li>
</ul>

<p>This documentation will guide you through the setup process and help you make the most of AITradeStrategist's powerful features.</p>
`,
        order: 1
    },
    'getting-started-installation': {
        category: 'getting-started',
        title: 'Installation',
        content: `
<h2>Installation Guide</h2>

<h3>System Setup</h3>
<p>AITradeStrategist requires a few components to run properly:</p>

<h4>Required Components:</h4>
<ol>
    <li><strong>Python Environment:</strong> Python 3.8 or newer</li>
    <li><strong>Database:</strong> PostgreSQL database</li>
    <li><strong>GPU Support (Optional):</strong> AMD GPU with ROCm or DirectML support</li>
</ol>

<h3>Installation Steps</h3>

<h4>1. Clone the Repository</h4>
<pre><code>git clone https://github.com/username/aitradestrategist.git
cd aitradestrategist</code></pre>

<h4>2. Install Dependencies</h4>
<pre><code>pip install -r requirements.txt</code></pre>

<h4>3. Configure Database</h4>
<p>Update the .env file with your PostgreSQL database credentials:</p>
<pre><code>DATABASE_URL=postgresql://username:password@localhost:5432/aitradestrategist</code></pre>

<h4>4. Initialize Database</h4>
<pre><code>python initialize_db.py</code></pre>

<h4>5. Start the Application</h4>
<pre><code>python main.py</code></pre>

<h3>GPU Acceleration Setup</h3>

<h4>For AMD GPUs with DirectML:</h4>
<ol>
    <li>Install the latest AMD GPU drivers</li>
    <li>Install DirectML package: <code>pip install lightgbm-directml</code></li>
    <li>Enable GPU acceleration in Settings</li>
</ol>

<h3>Connecting to Freqtrade</h3>
<p>To enable live trading capabilities, you need to connect AITradeStrategist to your Freqtrade instance:</p>
<ol>
    <li>Set up Freqtrade with REST API enabled</li>
    <li>Generate an API key in your Freqtrade configuration</li>
    <li>Enter the Freqtrade API URL and key in the Settings page</li>
</ol>

<h3>Troubleshooting</h3>
<p>If you encounter any issues during installation:</p>
<ul>
    <li>Check the logs for detailed error messages</li>
    <li>Ensure all dependencies are properly installed</li>
    <li>Verify database connection settings</li>
    <li>For GPU-related issues, check that your GPU drivers are up to date</li>
</ul>
`,
        order: 2
    },
    'getting-started-quick-start': {
        category: 'getting-started',
        title: 'Quick Start Guide',
        content: `
<h2>Quick Start Guide</h2>

<p>This guide will help you get up and running with AITradeStrategist in just a few minutes.</p>

<h3>Step 1: Dashboard Overview</h3>
<p>After logging in, you'll see the main dashboard which displays:</p>
<ul>
    <li>Performance summary</li>
    <li>Active trading models</li>
    <li>Recent trades</li>
    <li>System status</li>
</ul>

<p>Spend some time exploring the dashboard to get familiar with the available information.</p>

<h3>Step 2: Configure Settings</h3>
<ol>
    <li>Navigate to the <strong>Settings</strong> page</li>
    <li>Configure your trading parameters (stake amount, max open trades, etc.)</li>
    <li>Set up Freqtrade connection if you want to enable live trading</li>
    <li>Configure your preferred risk level and notification settings</li>
    <li>Save your settings</li>
</ol>

<h3>Step 3: Review Existing Models</h3>
<ol>
    <li>Go to the <strong>Models</strong> page</li>
    <li>Explore the pre-configured trading models</li>
    <li>Review their performance metrics and parameters</li>
</ol>

<h3>Step 4: Run Your First Backtest</h3>
<ol>
    <li>Select a model from the Models page</li>
    <li>Click "Backtest" to evaluate its performance on historical data</li>
    <li>Review the results in the Performance Analysis page</li>
</ol>

<h3>Step 5: Deploy a Model (Optional)</h3>
<p>If you're satisfied with a model's performance:</p>
<ol>
    <li>Click "Activate" on the model's card</li>
    <li>Confirm your selection</li>
    <li>The model will now be used for generating trading signals</li>
</ol>

<h3>Step 6: Monitor Performance</h3>
<ol>
    <li>Return to the Dashboard to monitor your trading activity</li>
    <li>Use the Performance page for more detailed analysis</li>
    <li>Check the Recent Trades section to see your model in action</li>
</ol>

<h3>Next Steps</h3>
<p>After getting familiar with the basic functionality, you can:</p>
<ul>
    <li>Create custom trading models</li>
    <li>Experiment with different trading strategies</li>
    <li>Fine-tune model parameters</li>
    <li>Explore strategy recommendations</li>
    <li>Generate detailed performance reports</li>
</ul>

<p>Refer to the specific documentation sections for more detailed information on each feature.</p>
`,
        order: 3
    },
    
    // Dashboard section
    'dashboard-overview': {
        category: 'dashboard',
        title: 'Dashboard Overview',
        content: `
<h2>Dashboard Overview</h2>

<p>The Dashboard provides a comprehensive overview of your trading activity, model performance, and system status. It's designed to give you quick insights into your trading operation.</p>

<h3>Key Components</h3>

<h4>1. Performance Summary</h4>
<p>At the top of the dashboard, you'll find key performance metrics:</p>
<ul>
    <li><strong>Total Trades:</strong> The total number of completed trades</li>
    <li><strong>Win Rate:</strong> Percentage of profitable trades</li>
    <li><strong>Profit:</strong> Overall profit percentage</li>
    <li><strong>Profit (USDT):</strong> Absolute profit in USDT</li>
</ul>

<h4>2. Performance Charts</h4>
<p>The dashboard includes two main charts:</p>
<ul>
    <li><strong>Performance Over Time:</strong> Shows cumulative profit over time</li>
    <li><strong>Performance By Pair:</strong> Shows profit distribution across different trading pairs</li>
</ul>

<h4>3. Recent Trades</h4>
<p>A table showing your most recent trading activity with details like:</p>
<ul>
    <li>Trading pair</li>
    <li>Open and close dates</li>
    <li>Open and close prices</li>
    <li>Profit/loss</li>
    <li>Trade status (open/closed)</li>
</ul>

<h4>4. System Information</h4>
<p>On the sidebar, you can see:</p>
<ul>
    <li><strong>GPU Status:</strong> Indicates if GPU acceleration is available</li>
    <li><strong>Freqtrade Status:</strong> Shows connection status to Freqtrade</li>
</ul>

<h3>Actions</h3>
<p>From the dashboard, you can:</p>
<ul>
    <li><strong>Refresh Data:</strong> Update all dashboard information</li>
    <li><strong>Navigate:</strong> Access other sections using the sidebar</li>
    <li><strong>Export:</strong> Some panels allow exporting data for further analysis</li>
</ul>

<h3>Best Practices</h3>
<ul>
    <li>Check your dashboard regularly to stay informed about your trading performance</li>
    <li>Pay attention to win rate and profit trends to identify strategy effectiveness</li>
    <li>Use the refresh button to ensure you're seeing the most current data</li>
    <li>Investigate any significant changes in performance metrics</li>
</ul>
`,
        order: 1
    },
    'dashboard-key-metrics': {
        category: 'dashboard',
        title: 'Key Performance Metrics',
        content: `
<h2>Key Performance Metrics</h2>

<p>Understanding the performance metrics displayed on your dashboard is crucial for evaluating your trading strategy's effectiveness.</p>

<h3>Primary Metrics</h3>

<h4>Total Trades</h4>
<p>The total number of completed trades (both winning and losing).</p>
<ul>
    <li><strong>What it tells you:</strong> Trading activity level and sample size for statistical reliability</li>
    <li><strong>Target:</strong> A sufficient number to draw statistically significant conclusions (typically >30)</li>
</ul>

<h4>Win Rate</h4>
<p>The percentage of trades that resulted in profit.</p>
<ul>
    <li><strong>Formula:</strong> (Winning Trades ÷ Total Trades) × 100%</li>
    <li><strong>What it tells you:</strong> The reliability of your trading strategy</li>
    <li><strong>Target:</strong> Most successful strategies maintain >55% win rate</li>
    <li><strong>Context:</strong> Should be evaluated alongside average win/loss ratio</li>
</ul>

<h4>Profit Percentage</h4>
<p>The overall return on investment as a percentage.</p>
<ul>
    <li><strong>Formula:</strong> ((Current Value - Initial Value) ÷ Initial Value) × 100%</li>
    <li><strong>What it tells you:</strong> Overall performance of your trading strategy</li>
    <li><strong>Target:</strong> Should exceed traditional investment returns (>10% annually)</li>
</ul>

<h4>Absolute Profit</h4>
<p>The actual monetary profit in USDT or other base currency.</p>
<ul>
    <li><strong>What it tells you:</strong> Real financial impact of your trading</li>
    <li><strong>Context:</strong> Consider this alongside percentage metrics for full perspective</li>
</ul>

<h3>Advanced Metrics</h3>

<h4>Drawdown</h4>
<p>The maximum observed loss from a peak to a trough before a new peak is attained.</p>
<ul>
    <li><strong>What it tells you:</strong> Risk and volatility of your strategy</li>
    <li><strong>Target:</strong> Lower drawdowns indicate more stable strategies</li>
</ul>

<h4>Sharpe Ratio</h4>
<p>A measure of risk-adjusted return.</p>
<ul>
    <li><strong>Formula:</strong> (Return - Risk-Free Rate) ÷ Standard Deviation of Returns</li>
    <li><strong>What it tells you:</strong> How much excess return you receive for extra volatility</li>
    <li><strong>Target:</strong> >1 is acceptable, >2 is good, >3 is excellent</li>
</ul>

<h4>Recovery Factor</h4>
<p>The ratio of absolute profit to maximum drawdown.</p>
<ul>
    <li><strong>Formula:</strong> Absolute Profit ÷ Maximum Drawdown</li>
    <li><strong>What it tells you:</strong> How effectively the strategy recovers from losses</li>
    <li><strong>Target:</strong> >3 is generally considered good</li>
</ul>

<h3>Interpreting Metrics Together</h3>
<p>For a comprehensive evaluation, consider these metrics in combination:</p>
<ul>
    <li>A high win rate with small profits may be less effective than a lower win rate with larger average profits</li>
    <li>Good absolute profit with high drawdown suggests a risky strategy</li>
    <li>Compare Sharpe Ratio across different strategies to identify optimal risk-adjusted performance</li>
</ul>

<h3>Common Pitfalls</h3>
<ul>
    <li><strong>Recency Bias:</strong> Giving too much weight to recent performance</li>
    <li><strong>Small Sample Size:</strong> Drawing conclusions from too few trades</li>
    <li><strong>Ignoring Market Context:</strong> Failing to consider overall market conditions</li>
</ul>

<p>Remember that past performance doesn't guarantee future results. Always monitor metrics over time and be prepared to adjust strategies as needed.</p>
`,
        order: 2
    },
    
    // Add more documentation entries for each section...
    
    // FAQ section
    'faq-general': {
        category: 'faq',
        title: 'General Questions',
        content: `
<h2>Frequently Asked Questions</h2>

<h3>General Questions</h3>

<h4>What is AITradeStrategist?</h4>
<p>AITradeStrategist is an advanced cryptocurrency trading platform that combines artificial intelligence and machine learning with Freqtrade's trading capabilities. It helps traders develop, test, and deploy AI-powered trading strategies.</p>

<h4>Do I need technical knowledge to use this platform?</h4>
<p>While basic familiarity with trading concepts is helpful, AITradeStrategist is designed to be accessible to users with varying levels of technical knowledge. The interface is intuitive, and many features include built-in guidance.</p>

<h4>Is AITradeStrategist free to use?</h4>
<p>AITradeStrategist offers both free and premium tiers. Basic functionality is available at no cost, while advanced features such as custom model training and strategy recommendations require a subscription.</p>

<h4>Which cryptocurrencies are supported?</h4>
<p>AITradeStrategist supports all cryptocurrencies available on your connected exchange through Freqtrade. This typically includes major coins like BTC, ETH, XRP, as well as hundreds of altcoins.</p>

<h4>Is my trading data secure?</h4>
<p>Yes, we implement industry-standard security measures to protect your data. AITradeStrategist never has direct access to your exchange accounts - all trading is executed through Freqtrade's secure API connections.</p>

<h3>Technical Requirements</h3>

<h4>Do I need a GPU to use AITradeStrategist?</h4>
<p>No, a GPU is not required. However, having an AMD GPU with DirectML support will significantly accelerate model training. Without a GPU, the system will operate in CPU mode, which is slower for model training but fully functional.</p>

<h4>What's the recommended hardware configuration?</h4>
<p>For optimal performance:
<ul>
    <li>CPU: 4+ cores</li>
    <li>RAM: 8GB+ (16GB recommended)</li>
    <li>GPU: AMD GPU with 8GB+ VRAM (optional but recommended)</li>
    <li>Storage: SSD with at least 10GB free space</li>
</ul></p>

<h4>Which browsers are supported?</h4>
<p>AITradeStrategist works with all modern browsers, including Chrome, Firefox, Safari, and Edge. For the best experience, we recommend using the latest version of Chrome or Firefox.</p>

<h3>Trading and Strategy Questions</h3>

<h4>Can I use AITradeStrategist for live trading?</h4>
<p>Yes, by connecting AITradeStrategist to Freqtrade, you can deploy your strategies for live trading. We recommend thoroughly testing any strategy with backtesting and paper trading before using real funds.</p>

<h4>How accurate are the AI predictions?</h4>
<p>Prediction accuracy varies based on market conditions, the quality of training data, and model configuration. Our models typically achieve 60-75% directional accuracy in stable market conditions, but past performance does not guarantee future results.</p>

<h4>How often are models updated?</h4>
<p>By default, models are retrained every 24 hours to adapt to changing market conditions. You can adjust this interval in the settings based on your preferences and computational resources.</p>

<h4>Can I customize the trading strategies?</h4>
<p>Yes, AITradeStrategist offers extensive customization options. You can modify existing strategies, create new ones, adjust risk parameters, and fine-tune model hyperparameters.</p>
`,
        order: 1
    },
    'faq-troubleshooting': {
        category: 'faq',
        title: 'Troubleshooting',
        content: `
<h2>Troubleshooting</h2>

<h3>Connection Issues</h3>

<h4>I can't connect to Freqtrade</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Verify that your Freqtrade instance is running and the REST API is enabled</li>
    <li>Check that the API URL is correct in the Settings page</li>
    <li>Ensure your API key is valid and has appropriate permissions</li>
    <li>Check for any firewall or network restrictions that might block the connection</li>
</ol>

<h4>Database connection errors</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Verify your database credentials in the .env file</li>
    <li>Ensure PostgreSQL is running and accessible</li>
    <li>Check database logs for any specific error messages</li>
    <li>Try reconnecting to the database through the Settings page</li>
</ol>

<h3>Performance Issues</h3>

<h4>Model training is very slow</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>If you have an AMD GPU, ensure GPU acceleration is enabled in Settings</li>
    <li>Update your GPU drivers to the latest version</li>
    <li>Reduce the training data timeframe or feature count</li>
    <li>Consider upgrading your hardware if you frequently train complex models</li>
</ol>

<h4>Dashboard is loading slowly</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Reduce the date range for performance analysis</li>
    <li>Check your internet connection speed</li>
    <li>Clear your browser cache and cookies</li>
    <li>Try using a different browser</li>
</ol>

<h3>Model and Strategy Issues</h3>

<h4>My model has poor performance</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Ensure you have sufficient training data (at least 6 months recommended)</li>
    <li>Review feature selection for relevance to your trading pair</li>
    <li>Try different model hyperparameters or use the auto-optimization feature</li>
    <li>Consider market conditions - some strategies perform better in specific market types</li>
</ol>

<h4>Strategy stopped generating signals</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Check model status in the Models page</li>
    <li>Verify that Freqtrade is properly configured to use the model</li>
    <li>Review logs for any error messages</li>
    <li>Try reactivating the model or training a new one</li>
</ol>

<h3>Data and Reporting Issues</h3>

<h4>Export function isn't working</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Ensure you have data to export</li>
    <li>Check browser console for JavaScript errors</li>
    <li>Try a different export format (CSV, PDF, or image)</li>
    <li>Update your browser to the latest version</li>
</ol>

<h4>Charts are not displaying correctly</h4>
<p><strong>Solution:</strong></p>
<ol>
    <li>Refresh the page</li>
    <li>Clear browser cache</li>
    <li>Check if you have JavaScript enabled</li>
    <li>Try a different browser</li>
</ol>

<h3>Still Having Issues?</h3>
<p>If you're still experiencing problems after trying these solutions:</p>
<ol>
    <li>Check the application logs for detailed error messages</li>
    <li>Search the documentation for specific error codes</li>
    <li>Visit our community forum for help from other users</li>
    <li>Contact support with details about your issue, including steps to reproduce</li>
</ol>
`,
        order: 2
    }
};

// Function to set up the documentation system
function initDocumentation(containerId = 'documentation-container') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Documentation container not found:', containerId);
        return;
    }
    
    // Create documentation structure
    createDocumentationStructure(container);
    
    // Set up navigation events
    setupDocNavigation();
    
    // Load initial content
    const initialDoc = getInitialDocToShow();
    showDocContent(initialDoc);
}

// Function to create documentation structure
function createDocumentationStructure(container) {
    // Create sidebar and content areas
    const docHtml = `
        <div class="row">
            <div class="col-md-3">
                <div class="docs-sidebar">
                    <div class="mb-4">
                        <input type="search" class="form-control" id="doc-search" placeholder="Search documentation...">
                    </div>
                    <div id="doc-navigation"></div>
                </div>
            </div>
            <div class="col-md-9">
                <div class="docs-content" id="doc-content-area"></div>
            </div>
        </div>
    `;
    
    container.innerHTML = docHtml;
    
    // Build the navigation menu
    buildDocNavigation();
}

// Function to build documentation navigation
function buildDocNavigation() {
    const navContainer = document.getElementById('doc-navigation');
    if (!navContainer) return;
    
    // Create category groups
    const categories = Object.keys(docCategories).sort((a, b) => 
        docCategories[a].order - docCategories[b].order
    );
    
    let navHtml = '';
    
    for (const category of categories) {
        const catInfo = docCategories[category];
        
        // Create category header
        navHtml += `
            <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted text-uppercase">
                <span><i class="${catInfo.icon} me-2"></i>${catInfo.title}</span>
            </h6>
            <ul class="nav flex-column mb-2" id="nav-${category}">
        `;
        
        // Add documents for this category
        const docs = Object.keys(docContent)
            .filter(key => docContent[key].category === category)
            .sort((a, b) => docContent[a].order - docContent[b].order);
        
        for (const docKey of docs) {
            const doc = docContent[docKey];
            navHtml += `
                <li class="nav-item">
                    <a class="nav-link doc-link" href="#" data-doc-id="${docKey}">
                        ${doc.title}
                    </a>
                </li>
            `;
        }
        
        navHtml += `</ul>`;
    }
    
    navContainer.innerHTML = navHtml;
}

// Function to set up navigation event handlers
function setupDocNavigation() {
    // Handle document link clicks
    document.querySelectorAll('.doc-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const docId = e.target.getAttribute('data-doc-id');
            
            // Update active state
            document.querySelectorAll('.doc-link').forEach(l => l.classList.remove('active'));
            e.target.classList.add('active');
            
            // Show the selected document
            showDocContent(docId);
        });
    });
    
    // Handle search
    const searchInput = document.getElementById('doc-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (query.length < 2) {
                // Show all links if query is too short
                document.querySelectorAll('.doc-link').forEach(link => {
                    link.style.display = 'block';
                });
                return;
            }
            
            // Filter links based on search
            document.querySelectorAll('.doc-link').forEach(link => {
                const docId = link.getAttribute('data-doc-id');
                const doc = docContent[docId];
                
                if (doc.title.toLowerCase().includes(query) || 
                    doc.content.toLowerCase().includes(query)) {
                    link.style.display = 'block';
                } else {
                    link.style.display = 'none';
                }
            });
        });
    }
}

// Function to get initial document to show
function getInitialDocToShow() {
    // Check URL hash
    const hash = window.location.hash.substring(1);
    if (hash && docContent[hash]) {
        return hash;
    }
    
    // Default to first document
    return Object.keys(docContent)[0];
}

// Function to show document content
function showDocContent(docId) {
    const contentArea = document.getElementById('doc-content-area');
    if (!contentArea) return;
    
    const doc = docContent[docId];
    if (!doc) {
        contentArea.innerHTML = '<div class="alert alert-danger">Document not found</div>';
        return;
    }
    
    // Update URL hash without triggering navigation
    history.replaceState(null, null, `#${docId}`);
    
    // Set content
    contentArea.innerHTML = doc.content;
    
    // Set active state on nav
    document.querySelectorAll('.doc-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-doc-id') === docId) {
            link.classList.add('active');
        }
    });
    
    // Scroll to top
    contentArea.scrollTop = 0;
}

// Search documentation content
function searchDocumentation(query) {
    const results = [];
    
    if (!query || query.length < 2) {
        return results;
    }
    
    const normalizedQuery = query.toLowerCase().trim();
    
    // Search in all documents
    for (const docId in docContent) {
        const doc = docContent[docId];
        const category = docCategories[doc.category];
        
        // Check title and content
        if (doc.title.toLowerCase().includes(normalizedQuery) || 
            doc.content.toLowerCase().includes(normalizedQuery)) {
            
            results.push({
                id: docId,
                title: doc.title,
                category: category.title,
                categoryIcon: category.icon,
                snippet: getContentSnippet(doc.content, normalizedQuery)
            });
        }
    }
    
    return results;
}

// Get content snippet showing search match with context
function getContentSnippet(content, query, snippetLength = 150) {
    // Strip HTML tags
    const plainText = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    
    // Find position of query
    const position = plainText.toLowerCase().indexOf(query);
    if (position === -1) {
        // If not found in plain text (might be in HTML tags), return beginning
        return plainText.substring(0, snippetLength) + '...';
    }
    
    // Calculate snippet start and end positions
    const halfLength = Math.floor(snippetLength / 2);
    let start = Math.max(0, position - halfLength);
    let end = Math.min(plainText.length, position + query.length + halfLength);
    
    // Adjust to not cut words
    while (start > 0 && plainText[start] !== ' ') start--;
    while (end < plainText.length && plainText[end] !== ' ') end++;
    
    // Create snippet with ellipsis if needed
    let snippet = '';
    if (start > 0) snippet += '...';
    snippet += plainText.substring(start, end);
    if (end < plainText.length) snippet += '...';
    
    return snippet;
}

// Export documentation functions
window.docManager = {
    init: initDocumentation,
    search: searchDocumentation,
    showDocument: showDocContent,
    getCategories: () => Object.entries(docCategories).map(([id, cat]) => ({ id, ...cat }))
};