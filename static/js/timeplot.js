

function plotTime(data) {
    var ctx = document.getElementById("time-bar").getContext("2d");
    var myBarChart = new Chart(ctx).Bar(data);
    console.log(data);
}

$.get('gettime.json', plotTime);

// Other syntax tried/for later
    // var options = { legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"
    //               }
    // var ctx = new Chart(document.getElementById("time-bar").getContext("2d")).Bar(data);