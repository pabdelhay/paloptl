function plotChart(data){

    am4core.ready(function() {

        // Themes begin
        am4core.useTheme(am4themes_animated);
        // Themes end

        // Create chart instance
        var chart = am4core.create("chartdiv", am4charts.XYChart);


        chart.data =data;
        //chart.numberFormatter.numberFormat = "#.## '%'";



        // Create axes
var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
categoryAxis.dataFields.category = "year";
categoryAxis.renderer.grid.template.location = 0;

var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
//valueAxis.renderer.inside = true;
//valueAxis.renderer.labels.template.disabled = true;
valueAxis.min = 0;
valueAxis.numberFormatter = new am4core.NumberFormatter();
valueAxis.numberFormatter.numberFormat = "#.#";



        // Create series
//        function createSeries(field, name) {
//
//          // Set up series
//          var series = chart.series.push(new am4charts.ColumnSeries());
//          series.name = name;
//          series.dataFields.valueY = field;
//          series.dataFields.categoryX = "year";
//          series.sequencedInterpolation = true;
//          series.calculatePercent = true;
//
//          // Make it stacked
//          series.stacked = true;
//
//          // Configure columns
//          series.columns.template.width = am4core.percent(60);
//          series.columns.template.tooltipText = "[bold]{name}[/]\n[font-size:14px]{categoryX}: {valueY}";
//
//        // Configure legend
//          series.legendSettings.itemValueText = "{valueY.percent}%";
//
//          // Add label
//          var labelBullet = series.bullets.push(new am4charts.LabelBullet());
//          labelBullet.label.text = "{valueY}";
//          labelBullet.locationY = 0.5;
//          labelBullet.label.hideOversized = true;
//
//          return series;
//        }

        function createSeries(field, name) {

  // Set up series
  var series = chart.series.push(new am4charts.ColumnSeries());
  series.name = name;
  series.dataFields.valueY = field;
  series.dataFields.categoryX = "year";
  series.sequencedInterpolation = true;
  series.calculatePercent = true;
  //series.cursorTooltipEnabled = false;

  // Make it stacked
  series.stacked = true;
  // Configure columns
  series.columns.template.width = am4core.percent(60);
  series.columns.template.tooltipText = "[bold]{name}[/]\n[font-size:14px]{categoryX}: [bold]{valueY.percent}%[/] ({valueY}Mzn)";

  // Configure legend
  series.legendSettings.itemValueText = "{valueY.percent}%";

  // Add label
  var labelBullet = series.bullets.push(new am4charts.LabelBullet());
  labelBullet.label.text = "{valueY.percent}%";
  labelBullet.locationY = 0.5;
  labelBullet.label.fill = am4core.color("#fff");

  return series;
}


        createSeries("budget_operation", "Budget Operation");
        createSeries("budget_investment", "Budget Investment");
//        createSeries("execution_operation", "execution_operation");
//        createSeries("execution_investment", "Execution Investment");

        // Legend
        chart.legend = new am4charts.Legend();

    });

}





function getData(){

    var url = '/api/mozambique-sergio/expenses_per_year_slug_group/?slug=mozambique&group=functional&code=1';
    $.get(url,function (result) {
        plotChart(result);
         console.log(result);


    }).fail(function(){

        console.log("Error");


    });

}

$(document).ready(function(){

    getData();
});

$(document).on('change','#id_country',function(ev){

   var t= $('#id_country').val();
   console.log(t);
    getData();

})
