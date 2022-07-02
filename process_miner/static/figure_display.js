/**
 * Function to place the plotly figures sent by the server on the page
 * @param {*} response 
 */
function updateFigures(response) {
    var figure = JSON.parse(response.mostCommonStep);
    Plotly.newPlot('mostCommonNode', figure.data, figure.layout);
    figure = JSON.parse(response.successionHeatmap);
    Plotly.newPlot('successionHeatmap', figure.data, figure.layout);
    figure = JSON.parse(response.occurrenceHistogram);
    Plotly.newPlot('occurrenceHistogram', figure.data, figure.layout);
    figure = JSON.parse(response.averageExecutionChainTypeTime);
    Plotly.newPlot('averageExecutionChainTypeTime', figure.data, figure.layout);
}