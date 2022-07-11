function decisionInfoHeuristicMiner(nodeId, div, d) {
    let decisionPoint = nodeId.split("|")[1].split("-").length > 1;
    if (decisionPoint) {
        let source_node = nodeId.split("|")[0];
        generateDecisionDIV(source_node, div, d);
    } else {
        div.html("Not a decision point")
            .style("left", (d.pageX + 10) + "px")
            .style("top", (d.pageY - 15) + "px");
    }
    div.transition()
        .duration(50)
        .style("opacity", 1);
}

function decisionInfoAlphaMiner(nodeId, div, d) {
    let source_nodes = [];
    let destination_nodes = [];
    for (const trans of window.transitionList) {
        if (trans[0] === nodeId) {
            destination_nodes.push(trans[1])
        } else if (trans[1] === nodeId) {
            source_nodes.push(trans[0])
        }
    }
    let decisionPoint = destination_nodes.length > 1;
    if (decisionPoint) {
        let source_node = source_nodes[0];
        generateDecisionDIV(source_node, div, d);
    } else {
        div.html("Not a decision point")
            .style("left", (d.pageX + 10) + "px")
            .style("top", (d.pageY - 15) + "px");
    }
    div.transition()
        .duration(50)
        .style("opacity", 1);
}

function generateDecisionDIV(source_node, div, d) {
    let options = Object.keys(window.decisionInformation[source_node]['options']);
    let decisionString = "Decision Options: <br><table  class=\"table\">";
    decisionString += "<tr>";
    decisionString += "<th>Attribute</th>";
    for (const option of options) {
        decisionString += "<th>" + option + "</th>";
    }
    decisionString += "</tr>";
    for (const attribute of window.decisionInformation[source_node]['commonAttributes']) {
        decisionString += "<tr>";
        decisionString += "<td>" + attribute + "</td>";
        for (const option of options) {
            decisionString += "<td>" + window.decisionInformation[source_node]['options'][option]['equals'][attribute] + "</td>";
        }
        decisionString += "</tr>";
    }
    decisionString += "</table>";
    div.html(decisionString)
        .style("left", (d.pageX + 10) + "px")
        .style("top", (d.pageY - 15) + "px");
}