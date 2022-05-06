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


links = d3.csvParse("source,target,type\n" +
    "a,ae,all\n" +
    "ae,e,all\n" +
    "b,bfc,all\n" +
    "bfc,f,all\n" +
    "bfc,c,all\n" +
    "e,ef,all\n" +
    "ef,f,all\n" +
    "c,cd,all\n" +
    "cd,d,all\n" +
    "a,adb,all\n" +
    "d,adb,all\n" +
    "adb,b,all\n" +
    "Start,a,all\n" +
    "f,End,all"
)

loc_raw = d3.csvParse("loc,type\n" +
    "a,trans\n" +
    "b,trans\n" +
    "e,trans\n" +
    "f,trans\n" +
    "c,trans\n" +
    "d,trans\n" +
    "Start,trans\n" +
    "End,trans\n" +
    "ae,pos\n" +
    "bfc,pos\n" +
    "ef,pos\n" +
    "cd,pos\n" +
    "adb,pos")


types = Array.from(new Set(links.map(d => d.type)))
nodes = ['']
data = ({nodes: Array.from(loc_raw, (i) => ({id: i['loc'], type: i['type']})), links})
height = 600

function shape(type) {
    if (type = "trans") {
        return "square"
    } else {
        return "circle"
    }
}

color = d3.scaleOrdinal(types, d3.schemeCategory10)

function linkArc(d) {
    // Calculate Radius for curved lines
    // const r = Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
    const r = 0;
    if (d.target.type === "trans") {
        return `
        M${d.source.x},${d.source.y}
        A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
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