// Based on Example by the D3 Team (Mike Bostock) See License.txt

function chart(data, width, height, types, color, location, drag, linkArc) {
    const links = data.links.map(d => Object.create(d));
    const nodes = data.nodes.map(d => Object.create(d));

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-400))
        .force("x", d3.forceX())
        .force("y", d3.forceY());

    const svg = d3.create("svg")
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .style("font", "12px sans-serif");

    // Per-type markers, as they don't inherit styles.
    svg.append("defs").selectAll("marker")
        .data(types)
        .join("marker")
        .attr("id", d => `arrow-${d}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -0.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", color)
        .attr("d", "M0,-5L10,0L0,5");

    const link = svg.append("g")
        .attr("fill", "none")
        .attr("stroke-width", 1.5)
        .selectAll("path")
        .data(links)
        .join("path")
        .attr("stroke", d => color(d.type))
        .attr("marker-end", d => `url(${new URL(`#arrow-${d.type}`, location)})`)

    const node = svg.append("g")
        .attr("fill", "currentColor")
        .attr("stroke-linecap", "round")
        .attr("stroke-linejoin", "round")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .attr("class", function (d) {
            return d.type + " node";
        })
        .call(drag(simulation));

    // node.append("circle")
    //     .attr("stroke", "white")
    //     .attr("stroke-width", 1.5)
    //     .attr("r", 4);


    simulation.on("tick", () => {
        link.attr("d", linkArc);
        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // invalidation.then(() => simulation.stop());

    return svg.node();
}


function shape(type) {
    if (type = "trans") {
        return "square"
    } else {
        return "circle"
    }
}

function linkArc(d) {
    // Calculate Radius for curved lines
     const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
    //const r = 0;
    if (d.target.type === "trans") {
        // calculate correct point
        alpha = Math.tan((d.source.y - d.target.y) / (d.source.x - d.target.x))
        if (d.source.x <= d.target.x) {
            qx = d.target.x - 5
        } else {
            qx = d.target.x + 5
        }
        if (d.source.y <= d.target.y) {
            qy = d.target.y - Math.atan(alpha) * 5
        } else {
            qy = d.target.y + Math.atan(alpha) * 5
        }


        return `
        M${d.source.x},${d.source.y}
        A${r},${r} 0 0,1 ${qx},${qy}
  `;

    }
    return `
    M${d.source.x},${d.source.y}
    A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
  `;
}


drag = simulation => {

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
}

function removeDuplicates(arr) {
    return arr.filter((item,
                       index) => arr.indexOf(item) === index);
}

function loadPetrinet(locations, transitions) {
    console.log(locations);
    console.log(transitions);

    let links = removeDuplicates(d3.csvParse(transitions))

    let loc_raw = removeDuplicates(d3.csvParse(locations))
    console.log(loc_raw)

    let types = Array.from(new Set(links.map(d => d.type)))
    let nodes = ['']
    let data = ({nodes: Array.from(loc_raw, (i) => ({id: i['loc'], type: i['type']})), links})
    let height = 600
    let color = d3.scaleOrdinal(types, d3.schemeCategory10)
    // append the svg object to the body of the page
    let c = chart(data, 600, 400, types, color, location, drag, linkArc)

    console.log(c)
    document.getElementById("output").innerHTML = ""
    document.getElementById("output").append(c)

    var div = d3.select("body").append("div")
        .attr("class", "tooltip-petrinet")


    d3.selectAll(".trans").append("rect")
        .attr("data-id", function (d) {return d.id})
        .attr("width", 20)
        .attr("height", 20)
        .attr("stroke", 'black')
        .attr("fill", 'white')
        .attr("x", -10)
        .attr("y", -10)
        .attr("class", function (d) {
            return "node type " + d.type
        }).on('mouseover', function (d, i) {
        d3.select(this).transition()
            .duration('50')
            .attr('opacity', '.85');
        //Makes the new div appear on hover
        nodeId = d.target.getAttribute('data-id');
        div.transition()
            .duration(50)
            .style("opacity", 1);
        div.html("<b>" +window.nodeStats[nodeId]['name'] + "</b><br>Occurrences: " +window.nodeStats[nodeId]['countOccurence'] + "<br> Latest Occurrence: " + window.nodeStats[nodeId]['latestOccurence'])
            .style("left", (d.pageX + 10) + "px")
            .style("top", (d.pageY - 15) + "px");
        }).on('mouseout', function (d, i) {
            d3.select(this).transition()
                .duration('50')
                .attr('opacity', '1');
            div.transition()
                .duration('50')
                .style("opacity", 0);
        });

    d3.selectAll(".pos").append("circle")
        .attr("stroke", "black")
        .attr("stroke-width", 1.5)
        .attr("fill", 'white')
        .attr("r", 4);

    d3.selectAll(".se").append("circle")
        .attr("stroke", "black")
        .attr("stroke-width", 1.5)
        .attr("fill", 'black')
        .attr("r", 6);


    d3.selectAll(".se").append("text")
        .attr("x", 6)
        .attr("y", 12)
        .text(d => d.id)
        .clone(true).lower()
        .attr("fill", "none")
        .attr("stroke", "white")
        .attr("stroke-width", 3);


    if (window.debugState) {
        d3.selectAll(".pos").append("text")
            .attr("x", -2)
            .attr("y", 2)
            .text(d => d.id)
            .clone(true).lower()
            .attr("fill", "none")
            .attr("stroke", "white")
            .attr("stroke-width", 3);
    }


    d3.selectAll(".trans").append("text")
        .attr("x", -2)
        .attr("y", 2)
        .text(function (d) {
            if (d.id.length <= 2) {
                return d.id;
            } else {
                window.legend.push(d.id);
                return "q" + window.legend.length;
            }

        })
        .clone(true).lower()
        .attr("fill", "none")
        .attr("stroke", "white")
        .attr("stroke-width", 3);
}