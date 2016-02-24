
function plotAllTimeData(data) {

    var nPlots = data['all_plots'].length;

    for(var i=0; i<nPlots; i++){
        $('#all-plots').append("<canvas id=\"plot" + i + "\" width=\"900\" height=\"400\"></canvas><div id=\"legend-plot" + i + "\" class=\"bar-legend\"></div>");

        var options = {legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                      };

        var ctx = document.getElementById(("plot"+i)).getContext("2d");
        var myBarChart = new Chart(ctx).Bar(data['all_plots'][i], options);
        $(("#legend-plot" + i)).html(myBarChart.generateLegend());
    }

}

$.get('gettime.json', plotAllTimeData);
