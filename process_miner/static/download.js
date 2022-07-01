$("#svg_download").click(function () {
    console.log("Saving File");
    var svgData = $("#svgCanvas").html();
    var head = '<svg title="graph" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="-300,-200,600,400">'
    var svgWhole = head + svgData + "</svg>";
    var svgBlob = new Blob([svgWhole], {type: "image/svg+xml;charset=utf-8"});
    saveAs(svgBlob, "output.svg");
    // var svgUrl = URL.createObjectURL(svgBlob);
    // var downloadLink = document.createElement("a");
    // downloadLink.href = svgUrl;
    // downloadLink.download = "output.svg";
    // document.body.appendChild(downloadLink);
    // downloadLink.click();
    // document.body.removeChild(downloadLink);
})