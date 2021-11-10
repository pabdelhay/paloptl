
function plotChart(data){

    am4core.useTheme(am4themes_animated);

    // Create chart instance
    var chart = am4core.create("chartdiv", am4charts.XYChart);
    chart.data = data;

    chart.colors.list = [
        am4core.color("#0F69A3"),
        am4core.color("#98B8DA"),
        am4core.color("#C90000"),
        am4core.color("#FF8080")
    ];
    chart.zoomOutButton.disabled = true;
    chart.numberFormatter.bigNumberPrefixes = [
        {"number": 1e+3, "suffix": "K"},
        {"number": 1e+6, "suffix": "Mi"},
        {"number": 1e+9, "suffix": "Bi"},
        {"number": 1e+12, "suffix": "Tri"},
        {"number": 1e+15, "suffix": "Qua"}
        /*{"number": 1e+18, "suffix": "E"},
        {"number": 1e+21, "suffix": "Z"},
        {"number": 1e+24, "suffix": "Y"}*/
    ];
    // Create axes
    var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "year";
    categoryAxis.title.text = "Local country offices";
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.minGridDistance = 20;
    categoryAxis.renderer.cellStartLocation = 0.2;
    categoryAxis.renderer.cellEndLocation = 0.8;

    var  valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.min = 0;
    valueAxis.title.text = "Expenditure (M)";
    valueAxis.numberFormatter.numberFormat = "#. a";
    // Create series
    function createSeries(field, name, width, dx, dy, group) {
        var series = chart.series.push(new am4charts.ColumnSeries());
        series.dataFields.valueY = field;
        series.dataFields.categoryX = "year";
        series.name = name;
        if(field == "budget_revenue"){
            series.columns.template.tooltipText = "{name}: [bold]{valueY}[/] {budget_revenue_group}" ;
        }else if(field == "budget_expense"){
            series.columns.template.tooltipText = "{name}: [bold]{valueY}[/] {budget_expense_group}" ;
        }else{
            series.columns.template.tooltipText = "{name}: [bold]{valueY}[/]" ;
        }

        series.clustered = false;
        series.dx = dx;
        series.columns.template.width = width;
        series.numberFormatter.numberFormat = "###";
      // Label
        var bullet = series.bullets.push(new am4charts.LabelBullet());
        bullet.interactionsEnabled = false;
        bullet.dx = dx;
        bullet.dy = dy;
        bullet.fontSize = 15;
        bullet.label.verticalCenter = 'top';
        bullet.label.text = "{valueY.formatNumber('#.# a')}";
        bullet.label.fill = am4core.color('#0f2843');
        bullet.label.truncate = false;
    }

    createSeries("budget_revenue", "Receita", 60, -40);
    createSeries("execution_revenue", "Exec. Despesa", 40, -40);
    createSeries("budget_expense", "Despesa", 60, 40);
    createSeries("execution_expense", "Exec. Receita", 40, 40);
    // Add legend
    chart.legend = new am4charts.Legend();

}

function GetExpenseAndRevenue(country_id) {
    var url = "/api/budgets/budget_expense_revenue/?country=" + country_id;
    $.get(url, function (result) {
        plotChart(result);
    }).fail(function () {
        console.log("Error on fetching budget basic info.");
    });
}