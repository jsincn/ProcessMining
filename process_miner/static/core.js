/**
 * Core Display and upload functionality.
 *
 * Description.
 *
 * @link   URL
 * @file   This files defines the MyClass class.
 * @author AuthorName.
 * @since  x.x.x
 */
window.debugState = false;
$(document).ready(function () {
    $("#upload_button").click(function () {

        var fd = new FormData();
        var files = $('#xes_file')[0].files;
        var algorithm = $('#algorithmSelect').get(0).options[algorithmSelect.selectedIndex].text;
        var lifecycleTransition = $('#lifecycleTransition').get(0).value;
        if (files.length > 0) {
            fd.append('file', files[0]);
            fd.append('algorithm', algorithm);
            fd.append('lifecycleTransition', lifecycleTransition);
            // Show loading spinner
            d3.selectAll("#loadingSpinner").attr('hidden', null);
            d3.selectAll("#result_viewer").attr('hidden', true);
            $.ajax({
                url: 'api/upload',
                type: 'post',
                data: fd,
                contentType: false,
                processData: false,
                success: function (response) {
                    window.legend = [];
                    window.nodeStats = response.nodeStats;
                    window.decisionInformation = response.decisionInformation;
                    console.log(response);
                    if (response.algorithm === "Alpha Miner" || response.algorithm === "Alpha Plus Miner") {
                        // Run Alpha Miner Logic
                        window.transitionList = response.transitionList;
                        loadPetrinet(response.locations, response.transitions);
                        disableThresholdSliders();
                        updateTable(response);
                        updateFigures(response);
                        //
                    } else {
                        // Run Heuristic Miner Logic
                        window.dependencyMeasureMatrix = response.dependencyMeasureMatrix;
                        window.successionMatrix = response.successionMatrix;
                        window.alphabet = response.alphabet;
                        window.startNodes = response.start;
                        window.endNodes = response.end;
                        window.traces = response.l;
                        enableThresholdSliders(response.maxOccurrences);
                        const occurrenceThreshold = $("#occurrenceThresholdText").get(0).value;
                        const dependencyThreshold = $("#dependencyThresholdText").get(0).value;

                        updateHeuristicDisplay(response.dependencyMeasureMatrix, response.successionMatrix, response.l, response.alphabet, response.start, response.end, occurrenceThreshold, dependencyThreshold);
                        updateTable(response);
                        updateFigures(response);
                    }
                    // Hide loading Spinner
                    d3.selectAll("#result_viewer").attr('hidden', null);
                    d3.selectAll("#loadingSpinner").attr('hidden', true);
                },
            });
        } else {
            alert("Please select a file.");
        }
    });
});