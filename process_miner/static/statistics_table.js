function updateTable(response){
    $('#cache_run').text(response['cache']);
    $('#timestamp_run').text(response['timestamp']);
    $('#algorithm_run').text(response['algorithm']);
    $('#filename_run').text(response['filename']);
    $('#runtime_run').text(Math.round((response['runtime'] + Number.EPSILON) * 100) / 100 + " Seconds");
    $('#algorithm_metadata_table').html("");
    for (const property in response['meta']) {
        $('#algorithm_metadata_table').append("<tr>" +
            "<td>" + response['meta'][property]['name'] + "</td>" +
            "<td>" + response['meta'][property]['value'] + "</td>" +
            "</tr>");
    }
};