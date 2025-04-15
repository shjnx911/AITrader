/**
 * Report generation functions for AITradeStrategist
 * Supports CSV, PDF and image exports
 */

// Constants
const PDF_OPTIONS = {
    margin: 10,
    filename: 'trading_report.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
};

// Function to export data as CSV
function exportCSV(data, filename = 'trading_data.csv') {
    // Ensure we have data
    if (!data || !data.length) {
        console.error('No data to export');
        return false;
    }
    
    try {
        // Get headers from first object
        const headers = Object.keys(data[0]);
        
        // Create CSV content
        let csvContent = headers.join(',') + '\n';
        
        // Add rows
        data.forEach(item => {
            const row = headers.map(header => {
                // Handle commas and quotes in the data
                let cell = item[header] !== undefined && item[header] !== null ? item[header].toString() : '';
                if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                    cell = '"' + cell.replace(/"/g, '""') + '"';
                }
                return cell;
            });
            csvContent += row.join(',') + '\n';
        });
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        return true;
    } catch (error) {
        console.error('Error exporting CSV:', error);
        return false;
    }
}

// Function to export a chart as image
function exportChartAsImage(chartInstance, filename = 'chart.png') {
    try {
        // Get canvas and convert to URL
        const canvas = chartInstance.canvas;
        const url = canvas.toDataURL('image/png');
        
        // Create download link
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        link.click();
        
        return true;
    } catch (error) {
        console.error('Error exporting chart:', error);
        return false;
    }
}

// Function to export a chart as PDF
async function exportChartAsPDF(chartInstance, filename = 'chart.pdf') {
    try {
        // Get canvas and convert to image
        const canvas = chartInstance.canvas;
        const imgData = canvas.toDataURL('image/jpeg', 1.0);
        
        // Create PDF with jsPDF
        const pdf = new jspdf.jsPDF({
            orientation: 'landscape',
            unit: 'mm'
        });
        
        // Add chart title if available
        if (chartInstance.options.plugins && chartInstance.options.plugins.title && chartInstance.options.plugins.title.text) {
            pdf.setFontSize(16);
            pdf.text(chartInstance.options.plugins.title.text, 14, 22);
            pdf.setFontSize(12);
        }
        
        // Add image to PDF
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();
        const imgProps = pdf.getImageProperties(imgData);
        const imgHeight = (imgProps.height * pdfWidth) / imgProps.width;
        
        pdf.addImage(imgData, 'JPEG', 10, 30, pdfWidth - 20, imgHeight - 20);
        
        // Add date to footer
        const now = new Date();
        pdf.setFontSize(10);
        pdf.text(`Generated on ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`, 14, pdfHeight - 10);
        
        // Save PDF
        pdf.save(filename);
        
        return true;
    } catch (error) {
        console.error('Error exporting chart as PDF:', error);
        return false;
    }
}

// Function to generate a complete PDF report
async function generatePDFReport(reportTitle, chartInstances = [], tableData = null, additionalInfo = null) {
    try {
        // Create report container
        const reportContainer = document.createElement('div');
        reportContainer.style.width = '1000px';
        reportContainer.style.padding = '20px';
        reportContainer.style.backgroundColor = '#ffffff';
        reportContainer.style.color = '#000000';
        reportContainer.style.fontFamily = 'Arial, sans-serif';
        reportContainer.style.position = 'absolute';
        reportContainer.style.left = '-9999px';
        
        // Add title
        const title = document.createElement('h1');
        title.textContent = reportTitle;
        title.style.textAlign = 'center';
        title.style.marginBottom = '30px';
        reportContainer.appendChild(title);
        
        // Add date and time
        const dateInfo = document.createElement('p');
        const now = new Date();
        dateInfo.textContent = `Generated on ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`;
        dateInfo.style.textAlign = 'center';
        dateInfo.style.marginBottom = '30px';
        reportContainer.appendChild(dateInfo);
        
        // Add charts
        if (chartInstances && chartInstances.length) {
            const chartsContainer = document.createElement('div');
            chartsContainer.style.marginBottom = '30px';
            
            chartInstances.forEach((chart, index) => {
                // Create new canvas for the chart
                const canvas = document.createElement('canvas');
                canvas.width = chart.canvas.width;
                canvas.height = chart.canvas.height;
                
                // Copy chart to new canvas
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw chart on new canvas
                const chartImg = new Image();
                chartImg.src = chart.canvas.toDataURL('image/png');
                chartsContainer.appendChild(chartImg);
                
                // Add chart title if available
                if (chart.options.plugins && chart.options.plugins.title && chart.options.plugins.title.text) {
                    const chartTitle = document.createElement('h3');
                    chartTitle.textContent = chart.options.plugins.title.text;
                    chartTitle.style.textAlign = 'center';
                    chartsContainer.appendChild(chartTitle);
                }
                
                // Add spacing between charts
                if (index < chartInstances.length - 1) {
                    const spacer = document.createElement('div');
                    spacer.style.height = '30px';
                    chartsContainer.appendChild(spacer);
                }
            });
            
            reportContainer.appendChild(chartsContainer);
        }
        
        // Add table data if provided
        if (tableData) {
            const tableContainer = document.createElement('div');
            tableContainer.style.marginBottom = '30px';
            tableContainer.style.width = '100%';
            tableContainer.style.overflowX = 'auto';
            
            // Create table
            const table = document.createElement('table');
            table.style.width = '100%';
            table.style.borderCollapse = 'collapse';
            table.style.border = '1px solid #dddddd';
            
            // Add table header
            if (tableData.length > 0) {
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                
                Object.keys(tableData[0]).forEach(key => {
                    const th = document.createElement('th');
                    th.textContent = key;
                    th.style.padding = '8px';
                    th.style.border = '1px solid #dddddd';
                    th.style.backgroundColor = '#f2f2f2';
                    headerRow.appendChild(th);
                });
                
                thead.appendChild(headerRow);
                table.appendChild(thead);
                
                // Add table body
                const tbody = document.createElement('tbody');
                
                tableData.forEach((row, i) => {
                    const tr = document.createElement('tr');
                    tr.style.backgroundColor = i % 2 === 0 ? '#ffffff' : '#f9f9f9';
                    
                    Object.values(row).forEach(value => {
                        const td = document.createElement('td');
                        td.textContent = value;
                        td.style.padding = '8px';
                        td.style.border = '1px solid #dddddd';
                        tr.appendChild(td);
                    });
                    
                    tbody.appendChild(tr);
                });
                
                table.appendChild(tbody);
            }
            
            tableContainer.appendChild(table);
            reportContainer.appendChild(tableContainer);
        }
        
        // Add additional information if provided
        if (additionalInfo) {
            const infoContainer = document.createElement('div');
            infoContainer.style.marginBottom = '30px';
            
            if (typeof additionalInfo === 'string') {
                infoContainer.textContent = additionalInfo;
            } else {
                // Assume it's HTML content
                infoContainer.innerHTML = additionalInfo;
            }
            
            reportContainer.appendChild(infoContainer);
        }
        
        // Add to document
        document.body.appendChild(reportContainer);
        
        // Generate PDF
        await html2pdf()
            .from(reportContainer)
            .set(PDF_OPTIONS)
            .save();
        
        // Clean up
        document.body.removeChild(reportContainer);
        
        return true;
    } catch (error) {
        console.error('Error generating PDF report:', error);
        return false;
    }
}

// Function to load required dependencies
function loadReportDependencies() {
    return new Promise((resolve, reject) => {
        // Check if dependencies are already loaded
        if (window.html2pdf && window.jspdf) {
            resolve();
            return;
        }
        
        // Load html2pdf.js
        const html2pdfScript = document.createElement('script');
        html2pdfScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
        html2pdfScript.async = true;
        
        // Load jspdf.js if needed for direct chart export
        const jspdfScript = document.createElement('script');
        jspdfScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        jspdfScript.async = true;
        
        // Count loaded scripts
        let loadedCount = 0;
        const scriptCount = 2;
        
        const checkIfAllLoaded = () => {
            loadedCount++;
            if (loadedCount === scriptCount) {
                resolve();
            }
        };
        
        html2pdfScript.onload = checkIfAllLoaded;
        jspdfScript.onload = checkIfAllLoaded;
        
        html2pdfScript.onerror = (error) => reject(new Error(`Failed to load html2pdf: ${error}`));
        jspdfScript.onerror = (error) => reject(new Error(`Failed to load jspdf: ${error}`));
        
        document.head.appendChild(html2pdfScript);
        document.head.appendChild(jspdfScript);
    });
}

// Export report generation functions
window.reportManager = {
    generatePDFReport,
    exportCSV,
    exportChartAsImage,
    exportChartAsPDF,
    loadReportDependencies
};