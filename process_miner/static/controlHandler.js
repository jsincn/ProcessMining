// Based on the solution by Vasyl Vaskivskyi
// https://stackoverflow.com/questions/23218174/how-do-i-save-export-an-svg-file-after-creating-an-svg-with-d3-js-ie-safari-an

$("#svg_download").click(function () {
    console.log("Saving File");
    var svgData = $("#svgCanvas").html();
    var head = '<svg title="graph" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="-300,-200,600,400">'
    var svgWhole = head + svgData + "</svg>";
    var svgBlob = new Blob([svgWhole], {type: "image/svg+xml;charset=utf-8"});
    saveAs(svgBlob, "output.svg");
})

$("#print_report").click(function () {
    print();
})

$("#debugStateSwitch").change(function (){
    var checkedValue = $('#debugStateSwitch:checked').val();
    if (checkedValue === "on") {
        console.warn("Debug Mode Enabled!");
        window.debugState = true;
    } else {
        console.warn("Debug Mode Disabled!");
        window.debugState = false;
    }
})