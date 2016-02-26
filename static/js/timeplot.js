
function plotAllTimeData(data) {

    var nPlots = data['all_plots'].length;

    for(var i=0; i<nPlots; i++){

        var titleColumnHtml = "<div class='col-xs-12 col-md-12'>";
        var canvasColumnHtml = "<div class='col-xs-12 col-md-9'>";
        var legendColumnHtml = "<div class='col-xs-6 col-md-3'>";
        var canvasHtml = "<canvas id=\"plot" + i + "\" width=\"750\" height=\"300\"></canvas>";
        var legendHtml = "<div id=\"legend-plot" + i + "\" class=\"bar-legend\"></div>";

        var title = data['all_labels'][i];
        var titleHtml = '<h5>' + title + '</h5>';

        var plotHtml = ("<div class='row'>" +
                        titleColumnHtml + titleHtml + '</div>' +
                        canvasColumnHtml + canvasHtml + '</div>' +
                        legendColumnHtml + legendHtml + '</div>' +
                        '</div>');

        $('#all-plots').append(plotHtml);

        var options = {legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
                      };

        var ctx = document.getElementById(("plot"+i)).getContext("2d");
        var myBarChart = new Chart(ctx).Bar(data['all_plots'][i], options);
        $(("#legend-plot" + i)).html(myBarChart.generateLegend());
    }

}

$.get('gettime.json', plotAllTimeData);
