/**
 * Highly complicated function calculating the Splits and Joins of the heuristic miner in order to generate a petri-net
 * Can be argued whether this should be done in the frontend, but I do like the instance response it gives when changing the parameters (dependency measure and occurrence thresholds)
 * @param {object} dependencyMeasureMatrix
 * @param {object} successionMatrix
 * @param {list} traces
 * @param {list} alphabet
 * @param {list} start
 * @param {list} end
 * @param {float} occurrence_threshold
 * @param {float} dependency_threshold
 */
function updateHeuristicDisplay(dependencyMeasureMatrix, successionMatrix, traces, alphabet, start, end, occurrence_threshold, dependency_threshold) {

    // console.log(start);
    window.legend = [];
    var transitions = "source,target,type\n";
    var locations = "loc,type\n";
    var locs = []
    var trans = []
    for (const l of alphabet) {
        for (const r of alphabet) {
            if (successionMatrix[l][r] >= occurrence_threshold && dependencyMeasureMatrix[l][r] >= dependency_threshold) {
                trans.push({'left': l, 'right': r})
            }
        }
    }

    // Helper function to compare two transitions
    function isEqual(f, s) {
        return JSON.stringify(f) === JSON.stringify(s);
    }

    // Generate empty objects for storing the I/O relations
    let inputs = {};
    let outputs = {};
    for (const letter of alphabet) {
        inputs[letter] = {};
        outputs[letter] = {};
    }

    for (const trace of traces) {
        // Analyze all traces

        var trace_l_out = new Array(trace.length);
        var trace_l_in = new Array(trace.length);
        for (let ix = 0; ix < trace_l_in.length; ix++) {
            trace_l_in[ix] = [];
            trace_l_out[ix] = [];
        }
        // Generate causality relations for individual traces - Greedy Algorithm!
        // First from the back, then forwards
        // Weijters, A. & Ribeiro, Joel. (2011). Flexible Heuristics Miner (FHM). Journal of Applied Physiology - J APPL PHYSIOL. 310-317. 10.1109/CIDM.2011.5949453.
        for (let i = trace.length - 1; i >= 0; i--) {
            for (let j = i; j >= 0; j--) {
                if (trans.some(e => isEqual(e, {'left': trace[j], 'right': trace[i]}))) {
                    // if (trace[j] === trace[i]) {
                    //     break;
                    // }
                    if (!trace_l_out[j].includes(trace[i])) {
                        trace_l_out[j].push(trace[i]);
                    }
                    if (!trace_l_in[i].includes(trace[j])) {
                        trace_l_in[i].push(trace[j]);
                    }
                    break;
                }
            }
        }

        // Generate causality relations for individual traces - Greedy Algorithm!
        // Now do the same from the front
        for (let i = 0; i < trace.length; i++) {
            if (trace_l_out[i].length < 1) {
                for (let j = i; j < trace.length; j++) {
                    if (trans.some(e => isEqual(e, {'left': trace[i], 'right': trace[j]}))) {
                        // if (trace[j] === trace[i]) {
                        //     break;
                        // }
                        if (!trace_l_out[i].includes(trace[j])) {
                            trace_l_out[i].push(trace[j]);
                        }
                        if (!trace_l_in[j].includes(trace[i])) {
                            trace_l_in[j].push(trace[i]);
                        }
                        break;
                    }
                }
            }
        }

        // Append the current trace relations to the input and output frequency table
        for (let i = 0; i < trace.length; i++) {
            trace_l_in[i].sort()
            trace_l_out[i].sort()
            if (inputs[trace[i]][trace_l_in[i]] !== undefined) {
                inputs[trace[i]][trace_l_in[i]] += 1;
            } else {
                inputs[trace[i]][trace_l_in[i]] = 1;
            }
            if (outputs[trace[i]][trace_l_out[i]] !== undefined) {
                outputs[trace[i]][trace_l_out[i]] += 1;
            } else {
                outputs[trace[i]][trace_l_out[i]] = 1;
            }
        }

    }


    // Add start and end positions
    locations += "Start,se\n" +
        "End,se\n";


    // Add transitions from the start to the starting transitions
    for (const s of start) {
        transitions += "Start," + s + ",all\n";
    }

    // Add transitions from the ending transitions to the end
    for (const e of end) {
        transitions += e + ",End,all\n";
    }

    console.log(inputs)
    console.log(outputs)
    // Identify splits and joins based on the number of input and outputs for each transition
    let places_simple = [];
    let places_xor_split = [];
    let places_xor_join = [];
    let keys;
    for (const letter of alphabet) {
        locations += letter + ",trans\n";
        console.log("Analyzing " + letter + " with outputs: " + Object.keys(outputs[letter]))
        keys = Object.keys(outputs[letter]);
        keys = keys.map(function (a) {
                console.log("filtering " + a)
                let cmp = a.split(",");
                if (cmp.length > 1) {
                    cmp = cmp.filter(r => r !== letter);
                }
                return cmp.join(",");
            }
        )
        console.log("Analyzing " + letter + " with cleaned outputs: " + keys)
        if (keys.length === 1) {
            // No XOR Split Necessary
            let components = keys[0].split(",");
            if (components.length < 2 && components.length > 0) {
                // Sequence Pattern
                places_simple.push(letter + "|" + keys[0] + "|" + 0)
            } else if (components.length > 1) {
                // AND Pattern
                for (const p of components) {

                    places_simple.push(letter + "|" + p + "|" + 0)
                }

            }
        } else {
            // XOR Split necessary
            let out_str = letter + "|"
            let sum = 0;
            for (const key of keys) {
                // if (key === letter) {
                //     continue;
                // }
                let components = key.split(",");
                console.log("Analyzing " + letter + " key " + key + " outputs: " + components)
                // if (components.length > 1) {
                //     components = components.filter(function (a) {
                //             return !(a === letter);
                //         }
                //     )
                // }
                console.log("Analyzing " + letter + " key " + key + " sanitized outputs: " + components)

                if (components.length < 2 && components.length > 0 && key.length > 0) {
                    components = components.filter(function (value) {
                        return !(value === key) || !(value === letter);
                    })
                    out_str += key + "-"
                    sum += outputs[letter][keys[0]];
                } else if (components.length > 1) {
                    out_str += "andsplit" + components.join("/") + "-";
                    locations += "andsplit" + components.join("/") + ",transH\n"
                    for (const c of components) {

                        places_simple.push("andsplit" + components.join("/") + "|" + c + "|" + 0)
                    }
                    sum += outputs[letter][keys[0]];
                }
            }
            out_str = out_str.slice(0, -1);
            out_str += "|";
            out_str += 0;
            places_xor_split.push(out_str);
            console.log("out_str" + out_str)
        }
    }
    console.log(places_xor_split)


    for (const letter of alphabet) {

        keys = Object.keys(inputs[letter]);
        keys = keys.map(function (a) {
                console.log("filtering " + a)
                let cmp = a.split(",");

                cmp = cmp.filter(r => r !== letter);

                return cmp.join(",");
            }
        );
        keys = keys.filter(a => a !== "");
        console.log("Analyzing " + letter + " with cleaned inputs: " + keys)

        if (keys.length === 1) {
            // No XOR Join Necessary
            // Nothing to do here
        } else {
            // XOR Join necessary
            let in_str = ""
            let sum = 0;
            for (const key of keys) {
                // if (key === letter) {
                //     continue;
                // }

                let components = key.split(",");
                console.log("Analyzing " + letter + " key " + key + " inputs: " + components)
                // if (components.length > 1) {
                //     components = components.filter(function (a) {
                //             return !(a === letter);
                //         }
                //     )
                // }
                console.log("Analyzing " + letter + " key " + key + " sanitized inputs: " + components)
                if (components.length < 2 && components.length > 0 && key.length > 0) {
                    // Join for just XOR of individual states
                    // components = components.filter(function (value) {
                    //     return !(value === key);
                    // })
                    in_str += key + "-"
                    sum += inputs[letter][keys[0]];
                    places_simple = places_simple.filter(function (value, index, array) {
                        let parts = value.split("|");
                        let dst_cmp = parts[1].split("-");
                        return !(parts[0] === key && dst_cmp.includes(letter));
                    })
                } else if (components.length > 1 && key.length > 0) {
                    // Join of both an XOR and an AND
                    in_str += "andjoin" + components.join("/") + "-";
                    locations += "andjoin" + components.join("/") + ",transH\n"
                    for (const c of components) {
                        places_simple.push(c + "|" + "andjoin" + components.join("/") + "|" + 1)
                    }
                    sum += inputs[letter][keys[0]];
                    places_simple = places_simple.filter(function (value, index, array) {
                        let parts = value.split("|");
                        let dst_cmp = parts[1].split("-");
                        return !(components.includes(parts[0]) && dst_cmp.includes(letter));
                    })
                }
            }
            in_str = in_str.slice(0, -1);
            if (in_str.length > 0) {
                in_str += "|" + letter + "|" + 1;
                places_xor_join.push(in_str);
            }
            console.log("in_str" + in_str)
        }
    }
    // console.log(places_simple)

    // Generate the location and transition csv strings from the different arrays
    // Only for the xor splits and joins that also contain a and split this has already been done
    for (const p of places_simple) {
        let cmp = p.split("|");
        if (cmp[1] !== "") {
            locations += p + ",pos\n";

            transitions += cmp[0] + "," + p + ",all\n";
            transitions += p + "," + cmp[1] + ",all\n";
        }
    }
    for (const p of places_xor_join) {
        let cmp = p.split("|");
        if (cmp[1] !== "") {
            locations += p + ",pos\n";
            let components = cmp[0].split("-")
            for (const c of components) {
                transitions += c + "," + p + ",all\n";
            }
            transitions += p + "," + cmp[1] + ",all\n";
        }
    }
    for (const p of places_xor_split) {
        let cmp = p.split("|");
        if (cmp[1] !== "") {
            locations += p + ",pos\n";
            let components = cmp[1].split("-")
            for (const c of components) {
                transitions += p + "," + c + ",all\n";
            }
            transitions += cmp[0] + "," + p + ",all\n";
        }
    }

    // Load the petrinet from the provided locations and transitions
    loadPetrinet(locations, transitions);
    // console.log(inputs);
    // console.log(outputs);

    // console.log("Transitions: " + trans)
}

/**
 * Updates the maxOccurences Slider and enables the sliders
 * @param {*} maxOccurrences
 */
function enableThresholdSliders(maxOccurrences) {
    d3.selectAll(".heuristicThresholds").attr('disabled', null);
    d3.selectAll(".occurrenceThreshold").attr('disabled', null);
    d3.selectAll(".occurrenceThreshold").attr('max', maxOccurrences);
}

/**
 * Disables the threshold sliders (e.g. when running the alpha algorithm)
 */
function disableThresholdSliders() {
    d3.selectAll(".heuristicThresholds").attr('disabled', true);
}


// Just some input handlers for the different thresholds
$("#occurrenceThresholdSlider").change(function () {
    $("#occurrenceThresholdText").get(0).value = $("#occurrenceThresholdSlider").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.traces, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});

$("#occurrenceThresholdText").change(function () {
    $("#occurrenceThresholdSlider").get(0).value = $("#occurrenceThresholdText").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.traces, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});
$("#dependencyThresholdSlider").change(function () {
    $("#dependencyThresholdText").get(0).value = $("#dependencyThresholdSlider").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.traces, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});

$("#dependencyThresholdText").change(function () {
    $("#dependencyThresholdSlider").get(0).value = $("#dependencyThresholdText").get(0).value;
    updateHeuristicDisplay(window.dependencyMeasureMatrix, window.successionMatrix, window.traces, window.alphabet, window.startNodes, window.endNodes, $("#occurrenceThresholdText").get(0).value, $("#dependencyThresholdText").get(0).value)

});
