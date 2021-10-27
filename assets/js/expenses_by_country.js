//BINDS
$(document).ready(function(){
    $(".year").click(function()
    {
        $(".year").css("background-color", "white");
        $(this).css("background-color", "yellow");
        get_chart_data($(this).text());
    });
});

//FUNCTIONS

function get_chart_data(year)
{
    var url = 'http://127.0.0.1:8000/api/budgets/expenses_by_country/?year=' + year;
    $.get(url, function (data) {
        var categories = data['categories'];
        var chart_data = data['data'];
        console.log(chart_data);
        plotChart(chart_data, categories);
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}
function get_expense_by_country(year)
{
    var url = 'http://127.0.0.1:8000/api/budgets/expenses_by_country/?year=' + year;
    $.get(url, function (data)
    {
        console.log(data);
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}

function budget_category_percentage(year)
{
    var url = '/api/budgets/budget_category_percentage/?category=saúde&year=' + year;
    console.log("url: " + url);
    $.get(url, function (data)
    {
        console.log(data);
        $('#list_countries').empty();
        for (var d in data)
        {
            var country = data[d];
            console.log(country);
            var p = country['percental'];
            p = p.toFixed(2);
            console.log("vvv" + p);
            var country_percent = country['country'] + " - " + (p * 100) + "%";
            $('#list_countries').append('<p>' + country_percent + '</p>')

        }
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}

function plotChart(data, categories)
{
    console.log(data);
    //GRAFICS

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
      series.calculatePercent = true; // enable to calculate percent

      // Make it stacked
      series.stacked = true;

      // Configure columns
      series.columns.template.width = am4core.percent(60);
      series.columns.template.tooltipText = "[bold]{name}[/]\n[font-size:14px]{categoryX}: {valueY.formatNumber('#.00')}%";

      // Add label
      var labelBullet = series.bullets.push(new am4charts.LabelBullet());
      labelBullet.label.text = "{valueY.formatNumber('#.00')}%";
      labelBullet.locationY = 0.5;
      labelBullet.label.hideOversized = true;

      return series;
    }
    categories.forEach(function(name){
        createSeries(name, name);
    });
//    createSeries("expense_health", "Saúde");
//    createSeries("expense_education", "Educação");
//    createSeries("expense_security", "Segurança");

    // Legend
    chart.legend = new am4charts.Legend();

}

get_chart_data(2018);