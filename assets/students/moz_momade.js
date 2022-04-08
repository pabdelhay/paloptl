function getOlaPython(){
    var url = '/api/mocambique-momade/year_percent_get_parameter/?slug=mozambique';
    $.get(url, function(result){

        plotchart(result)

        console.log(result)
    }).fail(function(){
        console.log("Error on fetching data.")
    });
}


$( document ).ready(function() {
   getOlaPython();
});


function plotchart(data){

    am4core.ready(function() {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end

    // Create chart instance
        var chart = am4core.create("chartdiv", am4charts.XYChart);

    // Add data
    chart.data = data

    // Create axes

    var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "year";
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.minGridDistance = 30;

    categoryAxis.renderer.labels.template.adapter.add("dy", function(dy, target) {
      if (target.dataItem && target.dataItem.index & 2 == 2) {
        return dy + 25;
      }
      return dy;
    });

    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

    // Create series
    var series = chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.valueY = "percent";
    series.dataFields.categoryX = "year";
    series.name = "percent";
    series.columns.template.tooltipText = "{categoryX}: [bold]{valueY}[/]";
    series.columns.template.fillOpacity = .8;


    // Create axes
    valueAxis.title.text = "Percentagem";
    valueAxis.title.fontWeight = "bold";




    var columnTemplate = series.columns.template;
    columnTemplate.strokeWidth = 2;
    columnTemplate.strokeOpacity = 1;

    }); // end am4core.ready()

}

