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

    function isEqual(f, s) {
        // console.log(f)
        // console.log(s)
        return JSON.stringify(f) === JSON.stringify(s);
    }

    // console.log("Something");
    let inputs = {};
    let outputs = {};
    for (const letter of alphabet) {
        inputs[letter] = {};
        outputs[letter] = {};
    }

    for (const trace of traces) {
        // console.log("Trace:" + trace);
        var trace_l_out = new Array(trace.length);
        var trace_l_in = new Array(trace.length);
        for (let ix = 0; ix < trace_l_in.length; ix++) {
            trace_l_in[ix] = [];
            trace_l_out[ix] = [];
        }


        for (let i = trace.length - 1; i >= 0; i--) {
            for (let j = i; j >= 0; j--) {
                // console.log("Trying " + trace[i] + " with " + trace[j])
                if (trans.some(e => isEqual(e, {'left': trace[j], 'right': trace[i]}))) {
                    // console.log("Found")
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

        for (let i = 0; i < trace.length; i++) {
            for (let j = i; j < trace.length; j++) {
                if (trans.some(e => isEqual(e, {'left': trace[i], 'right': trace[j]}))) {
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
        // console.log("trace_l_in:" + trace_l_in);
        // console.log("trace_l_out:" + trace_l_out);

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
        // console.log(inputs);
        // console.log(outputs);

    }


    locations += "Start,se\n" +
        "End,se\n";


    for (const s of start) {
        transitions += "Start," + s + ",all\n";
    }

    for (const e of end) {
        transitions += e + ",End,all\n";
    }

    let places_simple = [];
    let places_xor_split = [];
    let places_xor_join = [];
    let trans_inv = [];
    for (const letter of alphabet) {
        locations += letter + ",trans\n";
        if (Object.keys(outputs[letter]).length === 1) {
            // No XOR Split Necessary
            let components = Object.keys(outputs[letter])[0].split(",");
            if (components.length < 2 && components.length > 0) {
                // Sequence Pattern
                places_simple.push(letter + "|" + Object.keys(outputs[letter])[0] + "|" + outputs[letter][Object.keys(outputs[letter])[0]])
            } else if (components.length > 1) {
                // AND Pattern
                for (const p of components) {
                    places_simple.push(letter + "|" + p + "|" + outputs[letter][Object.keys(outputs[letter])[0]])
                }

            }
        } else {
            // XOR Split necessary
            let out_str = letter + "|"
            let sum = 0;
            for (const key of Object.keys(outputs[letter])) {
                let components = key.split(",");
                if (components.length < 2 && components.length > 0 && key.length > 0) {
                    components = components.filter(function (value) {
                        return !(value === key);
                    })
                    out_str += key + "-"
                    sum += outputs[letter][Object.keys(outputs[letter])[0]];
                } else if (components.length > 1) {
                    out_str += "and" + components.join("/") + "-";
                    locations += "and" + components.join("/") + ",trans\n"
                    for (const c of components) {
                        places_simple.push("and" + components.join("/") + "|" + c + "|" + outputs[letter][Object.keys(outputs[letter])[0]])
                    }
                    sum += outputs[letter][Object.keys(outputs[letter])[0]];
                }
            }
            out_str = out_str.slice(0, -1)
            out_str += "|"
            places_xor_split.push(out_str)
        }
    }

    for (const letter of alphabet) {
        if (Object.keys(inputs[letter]).length === 1) {
            // No XOR Join Necessary
            // Probably nothing to do here
            // let components = Object.keys(outputs[letter])[0].split(",");
            // if (components.length < 2 && components.length > 0) {
            //     // Sequence Pattern
            //     places_simple.push(letter + "|" + Object.keys(outputs[letter])[0] + "|" + outputs[letter][Object.keys(outputs[letter])[0]])
            // } else if (components.length > 1) {
            //     // AND Pattern
            //     for (const p of components) {
            //         places_simple.push(letter + "|" + p + "|" + outputs[letter][Object.keys(outputs[letter])[0]])
            //     }
            //
            // }
        } else {
            // XOR Join necessary
            let in_str = ""
            let sum = 0;
            for (const key of Object.keys(inputs[letter])) {
                let components = Object.keys(inputs[letter])[0].split(",");
                if (components.length < 2 && components.length > 0 && key.length > 0) {
                    components = components.filter(function (value) {
                        return !(value === key);
                    })
                    in_str += key + "-"
                    sum += inputs[letter][Object.keys(inputs[letter])[0]];
                    places_simple = places_simple.filter(function (value, index, array) {
                        let parts = value.split("|");
                        let dst_cmp = parts[1].split("-");
                        return !(parts[0] === key && dst_cmp.includes(letter));
                    })
                }
            }
            in_str = in_str.slice(0, -1);
            if (in_str.length > 0) {
                in_str += "|" + letter + "|" + sum;
                places_xor_join.push(in_str);
            }
        }
    }
    console.log(places_simple)
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


    console.log(inputs);
    console.log(outputs);
    loadPetrinet(locations, transitions);
    // console.log("Transitions: " + trans)
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
