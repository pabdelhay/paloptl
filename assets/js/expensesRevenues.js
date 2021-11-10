function getExpensesRevenuesAPI() {
    let url = "/api/budgets/expenses_and_revenues/?country=" + $(".country").attr("country_id");
    $.get(url, function (result) {
        plotChart(result);
    }).fail(function () {
        console.log("Error on fetching expenses and revenues.");
    });
}

let get_group = {
    "budget_revenue": "revenue_group",
    "execution_revenue": "revenue_group",
    "budget_expense": "expense_group",
    "execution_expense": "expense_group",
}

// Create series
function createSeries(field, name, width, dx, dy) {
    var series = chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.valueY = field;
    series.dataFields.categoryX = "year";
    series.name = name;
    if (name.toLowerCase().includes("despesa"))
        series.columns.template.tooltipText = `[bold]{year}[/]   [bold]{valueY}[/] ${name} de acordo com grupamento {expense_group}`;
    else
        series.columns.template.tooltipText = `[bold]{year}[/]  [bold]{valueY}[/] ${name} de acordo com grupamento {revenue_group}`;

    //series.columns.template.tooltipText = "{name}: [bold]{valueY}[/]";
    series.clustered = false;
    series.dx = dx;
    series.columns.template.width = width;

    let bullet = series.bullets.push(new am4charts.LabelBullet());
    bullet.interactionsEnabled = false;
    bullet.dy = dy;
    bullet.dx = dx;
    bullet.fontSize = 12;
    bullet.label.verticalCenter = 'top';
    bullet.label.text = "{valueY.formatNumber('#. a')}";
    bullet.label.fill = am4core.color('#0f2843');
    bullet.label.truncate = false;

    series.columns.template.tooltipText = `Ano: [bold]{year.formatNumber('#')}[/]
        Valor: [bold]{valueY.formatNumber('#,###')} ${$(".country").attr("cur")}[/]
        ${name} de acordo com grupamento [bold,italic]{${get_group[field]}}`;
}

var chart;

function plotChart(data) {
    chart = am4core.create("chartdiv", am4charts.XYChart);
    am4core.useTheme(am4themes_animated);
    chart.data = data;
    chart.colors.list = [
        am4core.color("#0F69A3"),
        am4core.color("#98B8DA"),
        am4core.color("#ea7a71"),
        am4core.color("#fbd1c1")
    ];
    chart.numberFormatter.bigNumberPrefixes = [
        {"number": 1e+3, "suffix": "K"},
        {"number": 1e+6, "suffix": "Mi"},
        {"number": 1e+9, "suffix": "Bi"},
        {"number": 1e+12, "suffix": "Tri"},
        {"number": 1e+15, "suffix": "Qua"},
        {"number": 1e+18, "suffix": "E"},
        {"number": 1e+21, "suffix": "Z"},
        {"number": 1e+24, "suffix": "Y"}
    ]
    // Create axes
    let categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = "year";
    categoryAxis.renderer.grid.template.location = 0;
    categoryAxis.renderer.minGridDistance = 20;
    categoryAxis.renderer.cellStartLocation = 0.2;
    categoryAxis.renderer.cellEndLocation = 0.8;
    categoryAxis.numberFormatter = new am4core.NumberFormatter();
    categoryAxis.numberFormatter.numberFormat = "###";
    categoryAxis.renderer.grid.template.disabled = true;

    let valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.min = 0;
    valueAxis.numberFormatter.numberFormat = "#. a";
    valueAxis.renderer.grid.template.disabled = true;

    createSeries("budget_revenue", "Dotação Receita", 50, -20, -30);
    createSeries("execution_revenue", "Execução Receita", 30, -20, 10);
    createSeries("budget_expense", "Dotação Despesa", 50, 30, -30);
    createSeries("execution_expense", "Execução Despesa", 30, 30, 10);
}

am4core.ready(function () {
    getExpensesRevenuesAPI();
});

