function PlotChart(category,data){
am4core.ready(function() {

// Themes begin
am4core.useTheme(am4themes_animated);
// Themes end

// Create chart instance
var chart = am4core.create("chartdiv", am4charts.XYChart);


// Add data
chart.data = data;

// Create axes
var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
categoryAxis.dataFields.category = "country";
categoryAxis.renderer.grid.template.location = 0;


var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
valueAxis.renderer.inside = true;
valueAxis.renderer.labels.template.disabled = true;
valueAxis.min = 0;

// Create series
function createSeries(field, name) {

  // Set up series
  var series = chart.series.push(new am4charts.ColumnSeries());
  series.name = name;
  series.dataFields.valueY = field;
  series.dataFields.categoryX = "country";
  series.sequencedInterpolation = true;

  // Make it stacked
  series.stacked = true;

  // Configure columns
  series.columns.template.width = am4core.percent(60);
  series.columns.template.tooltipText = "[bold]{name}[/]\n[font-size:14px]{categoryX}: {valueY}";

  // Add label
  var labelBullet = series.bullets.push(new am4charts.LabelBullet());
  //labelBullet.label.text = "{valueY}";
  labelBullet.label.text = "{valueY.formatNumber('#.00')}%";
  labelBullet.locationY = 0.5;
  labelBullet.label.hideOversized = true;

  return series;
}

var idx = 0;
for(;idx<category.length;idx++){
    createSeries(category[idx], category[idx]);
}

// Legend
chart.legend = new am4charts.Legend();

}); // end am4core.ready()
}


function GetPlotChart(year){
    var url = "/api/budgets/expense_by_country/?year="+year;
    $.get(url, function (result) {
        PlotChart(result.category,result.data);
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}



$(document).on('click', '.ano', function(ev){
    ev.preventDefault();
    var year = $(this).text();
    GetPlotChart(year)
});
