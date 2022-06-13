function updateHeuristicDisplay(dependencyMeasureMatrix, successionMatrix, alphabet, start, end, occurrence_threshold, dependency_threshold) {
    console.log(start);
    window.legend = [];
    var transitions = "source,target,type\n";
    var locations = "loc,type\n";
    var locs = []
    for (const l of alphabet) {

        for (const r of alphabet) {
            if (successionMatrix[l][r] >= occurrence_threshold && dependencyMeasureMatrix[l][r] >= dependency_threshold) {
                if (!locs.includes(l)) {
                    locations += l + ",trans\n";
                    locs.push(l)
                }
                if (!locs.includes(r)) {
                    locations += r + ",trans\n";
                    locs.push(r)
                }

                locations += l + r + ",pos\n";
                transitions += l + "," + l + r + ",all\n";
                transitions += l + r + "," + r + ",all\n";
            }
        }
    }
    locations += "Start,se\n" +
        "End,se";


    for (const s of start) {
        transitions += "Start," + s + ",all\n";
    }

    for (const e of end) {
        transitions += e + ",End,all\n";
    }


    console.log(locations);
    console.log(transitions);
    loadPetrinet(locations, transitions);
}


function enableThresholdSliders(maxOccurrences) {
    d3.selectAll(".heuristicThresholds").attr('disabled', null);
    d3.selectAll(".occurrenceThreshold").attr('max', maxOccurrences);
}

function disableThresholdSliders() {
    d3.selectAll(".heuristicThresholds").attr('disabled', true);
}


$("#occurrenceThresholdSlider").change(function () {

    $("#occurrenceThresholdText").get(0).value = $("#occurrenceThresholdSlider").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});

$("#occurrenceThresholdText").change(function () {
    $("#occurrenceThresholdSlider").get(0).value = $("#occurrenceThresholdText").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});
$("#dependencyThresholdSlider").change(function () {
    $("#dependencyThresholdText").get(0).value = $("#dependencyThresholdSlider").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});

$("#dependencyThresholdText").change(function () {
    $("#dependencyThresholdSlider").get(0).value = $("#dependencyThresholdText").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});
