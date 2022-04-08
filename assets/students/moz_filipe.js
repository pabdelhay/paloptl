function plotdata(data){
    am4core.ready(function() {

    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end

    // Create chart instance
    var chart = am4core.create("chartdiv", am4charts.XYChart);

    // Add percent sign to all numbers


    // Add data
    chart.data = data;
    // Create axes
    var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "year";
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.minGridDistance = 30;


    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.title.text = "Mozambique";
    valueAxis.title.fontWeight = 800;
    valueAxis.renderer.labels.template.adapter.add("text", function(text) {
    return text + "%";
    });
    // Create series

    var series2 = chart.series.push(new am4charts.ColumnSeries());
    series2.dataFields.valueY = "percent";
    series2.dataFields.categoryX = "year";
    series2.clustered = false;
    series2.columns.template.width = am4core.percent(80);
    series2.tooltipText = "Percentagem em {categoryX}: [bold]{valueY}[/]%";
    series2.numberFormatter.numberFormat = "#.#";

    chart.cursor = new am4charts.XYCursor();
    chart.cursor.lineX.disabled = true;
    chart.cursor.lineY.disabled = true;

    }); // end am4core.ready()
}

function getData(country){
    var url ='/api/mozambique-filipe/currency/?country='+ country;
    $.get(url, function(result){
        plotdata(result);
        console.log(result);
    }).fail(function(){
        console.log("Error");
    });
}
$(document).on('change','#id_country_choice',function (ev){
    var a = $("#id_country_choice").val();
    getData(a);
})
$( document ).ready(function(){
    getData();
});