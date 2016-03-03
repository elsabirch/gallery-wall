
function plotAllTimeData(data) {

    var nPlots = data['all_plots'].length;

    for(var i=0; i<nPlots; i++){

        var titleColumnHtml = "<div class='col-xs-12 col-sm-6 col-md-12'>";
        var canvasColumnHtml = "<div class='col-xs-12 col-sm-6 col-md-4 col-lg-4'>";
        var legendColumnHtml = "<div class='col-xs-6 col-md-3'>";
        var canvasHtml = "<canvas id=\"plot" + i + "\" width=\"300\" height=\"130\"></canvas>";
        var legendHtml = "<div id=\"legend-plot" + i + "\" class=\"bar-legend\"></div>";

        var title = data['all_labels'][i];
        var titleHtml = '<h6>' + title + '</h6>';

        var plotHtml = ( // "<div class='row'>" +
                        // titleColumnHtml + titleHtml + '</div>' +
                        // legendColumnHtml + legendHtml + '</div>' +

                        canvasColumnHtml + titleHtml + canvasHtml + '</div>'
                        // legendColumnHtml + legendHtml + '</div>' +
                        // +'</div>'
                        );

        var typeId = '#' + data['all_types'][i];
        $(typeId).append(plotHtml);

        var options = {legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>",
                       scaleOverride: true,
                        scaleSteps: 5,
                        scaleStepWidth: 0.2,
                        scaleStartValue: 0,
                        scaleShowLabels: false};

        var ctx = document.getElementById(("plot"+i)).getContext("2d");
        var myBarChart = new Chart(ctx).Bar(data['all_plots'][i], options);
        $(("#legend-plot" + i)).html(myBarChart.generateLegend());
    }

}

$.get('gettimespark.json', plotAllTimeData);
